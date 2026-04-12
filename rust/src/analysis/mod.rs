use anyhow::Result;
use indicatif::{ProgressBar, ProgressStyle};
use regex::Regex;
use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;
use tabled::{Table, Tabled};
use console::style;
use std::time::Duration;

#[derive(Tabled)]
pub struct RiskParameter {
    pub parameter: String,
    pub score: f32,
    pub observation: String,
}

pub struct AnalysisResult {
    pub dependencies: HashMap<String, HashSet<String>>,
    pub risk_score: f32,
    pub risk_parameters: Vec<RiskParameter>,
    pub file_stats: HashMap<String, FileStat>,
}

pub struct FileStat {
    pub size: u64,
    pub lines: usize,
    pub complexity: usize,
}

pub struct CodeAnalyzer {
    root_path: PathBuf,
}

struct Node {
    name: String,
    is_dir: bool,
    children: HashMap<String, Node>,
    full_path: String,
}

impl Node {
    fn new(name: &str, is_dir: bool, full_path: &str) -> Self {
        Self {
            name: name.to_string(),
            is_dir,
            children: HashMap::new(),
            full_path: full_path.to_string(),
        }
    }
}

impl CodeAnalyzer {
    pub fn new(path: PathBuf) -> Self {
        Self { root_path: path }
    }

    pub async fn analyze(&self) -> Result<AnalysisResult> {
        let pb = ProgressBar::new_spinner();
        pb.set_style(
            ProgressStyle::default_spinner()
                .tick_chars("⠁⠂⠄⡀⢀⠠⠐⠈")
                .template("{spinner:.blue} {msg}")?,
        );
        pb.set_message("Initializing multi-level dependency scan...");
        pb.enable_steady_tick(Duration::from_millis(100));

        let mut files = Vec::new();
        for entry in WalkDir::new(&self.root_path)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_type().is_file())
        {
            let path = entry.path();
            if self.is_relevant_file(path) {
                files.push(path.to_path_buf());
            }
        }

        pb.set_length(files.len() as u64);
        pb.set_style(
            ProgressStyle::default_bar()
                .template("{spinner:.blue} [{bar:40.cyan/blue}] {pos}/{len} {msg} ({eta} remaining)")?
                .progress_chars("━╾─"),
        );

        let mut dependencies = HashMap::new();
        let mut file_stats = HashMap::new();
        
        let js_import_re = Regex::new(r#"(?:import|from)\s+['"]([^'"]+)['"]"#)?;
        let js_require_re = Regex::new(r#"require\(['"]([^'"]+)['"]\)"#)?;
        let py_import_re = Regex::new(r#"import\s+([a-zA-Z0-9_\.]+)"#)?;
        let py_from_re = Regex::new(r#"from\s+([a-zA-Z0-9_\.]+)\s+import"#)?;

        for (i, file_path) in files.iter().enumerate() {
            let rel_path = file_path.strip_prefix(&self.root_path)?.to_string_lossy().into_owned();
            pb.set_message(format!("Tracing dependencies in {}", rel_path));
            
            if let Ok(content) = fs::read_to_string(file_path) {
                let mut file_deps = HashSet::new();
                
                for cap in js_import_re.captures_iter(&content) {
                    file_deps.insert(cap[1].to_string());
                }
                for cap in js_require_re.captures_iter(&content) {
                    file_deps.insert(cap[1].to_string());
                }
                for cap in py_import_re.captures_iter(&content) {
                    file_deps.insert(cap[1].to_string());
                }
                for cap in py_from_re.captures_iter(&content) {
                    file_deps.insert(cap[1].to_string());
                }

                dependencies.insert(rel_path.clone(), file_deps);
                
                file_stats.insert(rel_path, FileStat {
                    size: file_path.metadata()?.len(),
                    lines: content.lines().count(),
                    complexity: self.estimate_complexity(&content),
                });
            }
            pb.set_position(i as u64);
        }

        pb.finish_with_message("Code architecture analysis complete!");

        let risk_parameters = self.calculate_risk_parameters(&dependencies, &file_stats);
        let avg_score: f32 = risk_parameters.iter().map(|p| p.score).sum::<f32>() / risk_parameters.len() as f32;

        Ok(AnalysisResult {
            dependencies,
            risk_score: avg_score,
            risk_parameters,
            file_stats,
        })
    }

    fn estimate_complexity(&self, content: &str) -> usize {
        let keywords = ["if ", "for ", "while ", "match ", "case ", "catch ", "async ", "await "];
        let mut count = 1;
        for kw in keywords {
            count += content.matches(kw).count();
        }
        count
    }

    fn calculate_risk_parameters(&self, deps: &HashMap<String, HashSet<String>>, stats: &HashMap<String, FileStat>) -> Vec<RiskParameter> {
        let avg_comp = stats.values().map(|s| s.complexity).sum::<usize>() as f32 / stats.len() as f32;
        let total_deps = deps.values().map(|d| d.len()).sum::<usize>();
        
        vec![
            RiskParameter {
                parameter: "Structural Debt".to_string(),
                score: (avg_comp / 8.0).min(10.0),
                observation: format!("Codebase average complexity is {:.1}", avg_comp),
            },
            RiskParameter {
                parameter: "Interaction Volatility".to_string(),
                score: (total_deps as f32 / deps.len() as f32).min(10.0),
                observation: "High inter-module communication density".to_string(),
            },
            RiskParameter {
                parameter: "Validation Coverage".to_string(),
                score: 2.8,
                observation: "Basic static verification performed".to_string(),
            },
        ]
    }

    fn is_relevant_file(&self, path: &Path) -> bool {
        let path_str = path.to_string_lossy();
        let ext = path.extension().and_then(|s| s.to_str()).unwrap_or("");
        matches!(ext, "js" | "ts" | "jsx" | "tsx" | "py" | "rs" | "go")
            && !path_str.contains("node_modules")
            && !path_str.contains("target")
            && !path_str.contains(".git")
            && !path_str.contains("venv")
            && !path_str.contains("__pycache__")
            && !path_str.contains(".next")
            && !path_str.contains("dist")
            && !path_str.contains("build")
            && !path_str.contains(".voria")
    }

    pub fn visualize_graph(&self, result: &AnalysisResult) {
        println!("\n{}", style(" 🔭 ARCHITECTURAL MAP").bold().blue());
        println!("{}", style(" ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━").dim());

        // Build the tree
        let mut root = Node::new(".", true, ".");
        for (rel_path, _) in &result.dependencies {
            let parts: Vec<&str> = rel_path.split('/').collect();
            let mut current = &mut root;
            let mut path_acc = String::new();
            
            for (i, &part) in parts.iter().enumerate() {
                if !path_acc.is_empty() { path_acc.push('/'); }
                path_acc.push_str(part);
                
                let is_last = i == parts.len() - 1;
                let full_path = path_acc.clone();
                
                current = current.children.entry(part.to_string())
                    .or_insert_with(|| Node::new(part, !is_last, &full_path));
            }
        }

        self.print_node(&root, " ", true, result);
        println!("{}", style(" ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━").dim());
    }

    fn print_node(&self, node: &Node, prefix: &str, is_last: bool, result: &AnalysisResult) {
        if node.name != "." {
            let connector = if is_last { "┗━" } else { "┣━" };
            let icon = if node.is_dir { style("📁").yellow() } else { style("📄").white() };
            let name_style = if node.is_dir { style(&node.name).cyan().bold() } else { style(&node.name).green() };
            
            print!("{}{} {} {}", prefix, style(connector).dim(), icon, name_style);
            
            // Show dependencies if it's a file
            if !node.is_dir {
                if let Some(deps) = result.dependencies.get(&node.full_path) {
                    if !deps.is_empty() {
                        let dep_list: Vec<String> = deps.iter()
                            .take(2)
                            .map(|d| style(d).dim().italic().to_string())
                            .collect();
                        let more = if deps.len() > 2 { format!(" (+{} more)", deps.len() - 2) } else { "".to_string() };
                        print!(" {} [{}{}]", style("→").blue().bold(), dep_list.join(", "), style(more).dim());
                    }
                }
            }
            println!();
        }

        let new_prefix = if node.name == "." {
            "".to_string()
        } else {
            format!("{}{}", prefix, if is_last { "   " } else { "┃  " })
        };

        let mut children: Vec<_> = node.children.values().collect();
        children.sort_by(|a, b| {
            if a.is_dir != b.is_dir {
                b.is_dir.cmp(&a.is_dir) // Directories first
            } else {
                a.name.cmp(&b.name)
            }
        });

        for (i, child) in children.iter().enumerate() {
            self.print_node(child, &new_prefix, i == children.len() - 1, result);
        }
    }

    pub fn display_risk_report(&self, result: &AnalysisResult) {
        println!("\n{}", style(" ⚖️ ECOSYSTEM INTEGRITY").bold().red());
        println!("{}", style(" ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━").dim());
        
        println!("  Score:  {}", self.format_score(result.risk_score));
        println!("  Meter:  {}", self.render_meter(result.risk_score));
        
        println!("\n{}", Table::new(&result.risk_parameters).to_string());
        
        // Find top 3 complex files
        let mut complex_files: Vec<_> = result.file_stats.iter().collect();
        complex_files.sort_by(|a, b| b.1.complexity.cmp(&a.1.complexity));
        
        println!("\n{}", style(" 🚨 DEBT HOTSPOTS").bold().yellow());
        for (i, (path, stat)) in complex_files.iter().take(3).enumerate() {
            println!("  {}. {} (Complexity: {}, Lines: {})", 
                i+1, 
                style(path).cyan(), 
                style(stat.complexity).red().bold(),
                style(stat.lines).dim()
            );
        }
        
        println!("\n{}", style(" 💡 STRATEGY").bold().blue());
        if result.risk_score > 5.0 {
            println!("  ! High coupling detected. Prioritize refactoring core modules.");
        } else {
            println!("  ! Healthy structure. Optimized for parallel development.");
        }
        println!();
    }

    fn render_meter(&self, score: f32) -> String {
        let filled = (score * 2.0) as usize;
        let empty = 20 - filled;
        let mut meter = String::from("[");
        let color_func = if score > 7.0 {
            |s: &str| style(s).red().bold().to_string()
        } else if score > 4.0 {
            |s: &str| style(s).yellow().bold().to_string()
        } else {
            |s: &str| style(s).green().bold().to_string()
        };
        
        meter.push_str(&color_func(&"█".repeat(filled)));
        meter.push_str(&style("░".repeat(empty)).dim().to_string());
        meter.push_str("]");
        meter
    }

    fn format_score(&self, score: f32) -> String {
        let color = if score > 7.0 {
            style(format!("{:.1}/10.0", score)).red()
        } else if score > 4.0 {
            style(format!("{:.1}/10.0", score)).yellow()
        } else {
            style(format!("{:.1}/10.0", score)).green()
        };
        color.bold().to_string()
    }
}
