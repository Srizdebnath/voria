use std::io::Write;

use crate::config::Config;
use crate::ipc::{ProcessManager, Request, Response};
use crate::ui;
use anyhow::Result;
use colored::Colorize;

#[allow(dead_code)]
pub struct Orchestrator {
    config: Config,
    pm: ProcessManager,
}

impl Orchestrator {
    pub async fn new(config: Config) -> Result<Self> {
        let pm = ProcessManager::new(config.clone()).await?;
        Ok(Self { config, pm })
    }

    pub async fn process_responses(&mut self) -> Result<Response> {
        loop {
            let response = self.pm.read_response().await?;
            self.handle_response(&response).await?;

            if response.status == "success" || response.status == "error" {
                return Ok(response);
            }
        }
    }

    pub async fn plan(&mut self, issue_id: u64) -> Result<()> {
        ui::print_info(&format!("Planning fix for issue #{}", issue_id));

        let request = Request {
            command: "plan".to_string(),
            issue_id: Some(issue_id),
            repo_path: None,
            iteration: Some(1),
            extra: serde_json::json!({}),
        };

        self.pm.send_request(&request).await?;
        let _ = self.process_responses().await?;
        self.pm.stop().await?;
        Ok(())
    }

    pub async fn list_issues(&mut self, owner: &str, repo: &str) -> Result<()> {
        ui::print_info(&format!("Fetching issues from {}/{}", owner, repo));

        let request = Request {
            command: "list_issues".to_string(),
            issue_id: None,
            repo_path: Some(format!("{}/{}", owner, repo)),
            iteration: None,
            extra: serde_json::json!({
                "owner": owner,
                "repo": repo
            }),
        };

        self.pm.send_request(&request).await?;
        let _ = self.process_responses().await?;
        self.pm.stop().await?;
        Ok(())
    }

    pub async fn fix_issue(&mut self, owner: &str, repo: &str, issue_number: u64) -> Result<()> {
        ui::print_info(&format!(
            "Fixing issue #{} from {}/{}",
            issue_number, owner, repo
        ));

        let request = Request {
            command: "fix".to_string(),
            issue_id: Some(issue_number),
            repo_path: Some(format!("{}/{}", owner, repo)),
            iteration: Some(1),
            extra: serde_json::json!({
                "owner": owner,
                "repo": repo
            }),
        };

        self.pm.send_request(&request).await?;
        let _ = self.process_responses().await?;
        self.pm.stop().await?;
        Ok(())
    }

    pub async fn issue_loop(&mut self, issue_id: u64) -> Result<()> {
        ui::print_info(&format!("Starting issue loop for #{}", issue_id));

        let request = Request {
            command: "issue".to_string(),
            issue_id: Some(issue_id),
            repo_path: None,
            iteration: Some(1),
            extra: serde_json::json!({}),
        };

        self.pm.send_request(&request).await?;
        let _ = self.process_responses().await?;
        self.pm.stop().await?;
        Ok(())
    }

    pub async fn apply(&mut self, plan: &str) -> Result<()> {
        ui::print_info(&format!("Applying plan: {}", plan));

        let request = Request {
            command: "apply".to_string(),
            issue_id: None,
            repo_path: None,
            iteration: None,
            extra: serde_json::json!({
                "patch": plan
            }),
        };

        self.pm.send_request(&request).await?;
        let _ = self.process_responses().await?;
        self.pm.stop().await?;
        Ok(())
    }

    pub async fn list_tests(&mut self) -> Result<()> {
        ui::print_info("Listing available tests...");

        let request = Request {
            command: "list_tests".to_string(),
            issue_id: None,
            repo_path: None,
            iteration: None,
            extra: serde_json::json!({}),
        };

        self.pm.send_request(&request).await?;
        let response = self.process_responses().await?;

        if response.status == "success" {
            if let Some(tests) = response.extra.get("data").and_then(|d| d.get("tests")) {
                if let Some(tests_list) = tests.as_array() {
                    println!("\n{}", "  🔍 AVAILABLE VORIA TESTS".blue().bold());
                    println!("{}", "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue());
                    println!(
                        "  {:<25} │ {:<28} │ {:<13} │ {}",
                        "ID".blue().bold(),
                        "NAME".blue().bold(),
                        "CATEGORY".blue().bold(),
                        "IMPACT".blue().bold()
                    );
                    println!("{}", "  ─────────────────────────┼──────────────────────────────┼───────────────┼──────────".dimmed());
                    for t in tests_list {
                        let id = t["id"].as_str().unwrap_or("");
                        let name = t["name"].as_str().unwrap_or("");
                        let cat = t["category"].as_str().unwrap_or("");
                        let impact = t["impact"].as_str().unwrap_or("");
                        let impact_colored = match impact {
                            "critical" => impact.red().bold().to_string(),
                            "high" => impact.yellow().bold().to_string(),
                            "medium" => impact.cyan().to_string(),
                            _ => impact.dimmed().to_string(),
                        };
                        println!(
                            "  {:<25} │ {:<28} │ {:<13} │ {}",
                            id.bright_cyan(),
                            name.white(),
                            cat.blue(),
                            impact_colored
                        );
                    }
                    println!("{}", "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue());
                    println!(
                        "  {} tests available. Run: {}",
                        tests_list.len().to_string().blue().bold(),
                        "voria test <test_id>".bright_cyan()
                    );
                    println!();
                }
            }
        } else {
            ui::print_error(&response.message);
        }

        self.pm.stop().await?;
        Ok(())
    }

    pub async fn run_test(&mut self, test_id: &str) -> Result<()> {
        ui::print_info(&format!("Running test: {}", test_id));

        let request = Request {
            command: "test".to_string(),
            issue_id: None,
            repo_path: None,
            iteration: None,
            extra: serde_json::json!({
                "test_id": test_id
            }),
        };

        self.pm.send_request(&request).await?;
        let response = self.process_responses().await?;

        if response.status == "success" {
            if let Some(data) = response.extra.get("data").and_then(|d| d.get("result")) {
                self.display_test_report(test_id, data);
            } else {
                ui::print_success(&format!("Test '{}' completed.", test_id));
            }
        } else {
            ui::print_error(&response.message);
        }

        self.pm.stop().await?;
        Ok(())
    }

    fn display_test_report(&self, test_id: &str, data: &serde_json::Value) {
        let report = &data["result"];
        let status = report["status"].as_str().unwrap_or("unknown");

        println!(
            "\n{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );
        println!(
            "  {}",
            format!("📊 VORIA TEST REPORT: {}", test_id.to_uppercase())
                .blue()
                .bold()
        );
        println!(
            "{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );

        let status_display = match status {
            "passed" => "✓ PASSED".green().bold().to_string(),
            "failed" => "✗ FAILED".red().bold().to_string(),
            "warning" => "⚠ WARNING".yellow().bold().to_string(),
            _ => status.to_uppercase().dimmed().to_string(),
        };
        println!("  {:<15} : {}", "Status".blue().bold(), status_display);

        if let Some(score) = report["score"].as_f64() {
            let score_str = format!("{}/100", score);
            let score_colored = if score >= 80.0 {
                score_str.green().bold().to_string()
            } else if score >= 50.0 {
                score_str.yellow().bold().to_string()
            } else {
                score_str.red().bold().to_string()
            };
            println!(
                "  {:<15} : {}",
                "Security Score".blue().bold(),
                score_colored
            );
        }

        if let Some(summary) = report["summary"].as_str() {
            println!("\n  {}", "Summary:".blue().bold());
            for line in textwrap(summary, 70) {
                println!("  {}", line);
            }
        }

        if let Some(findings) = report["findings"].as_array() {
            if !findings.is_empty() {
                println!("\n  {}", "⚠  KEY FINDINGS:".yellow().bold());
                for f in findings.iter().take(10) {
                    let severity = f["severity"].as_str().unwrap_or("low");
                    let desc = f["description"].as_str().unwrap_or("");
                    let file = f["file"].as_str().unwrap_or("general");
                    let line = f["line"].as_u64().unwrap_or(0);

                    let sev_display = match severity {
                        "high" | "critical" => format!("[{}]", severity.to_uppercase())
                            .red()
                            .bold()
                            .to_string(),
                        "medium" => format!("[{}]", severity.to_uppercase())
                            .yellow()
                            .to_string(),
                        _ => format!("[{}]", severity.to_uppercase())
                            .dimmed()
                            .to_string(),
                    };
                    println!(
                        "    {} {} {}",
                        sev_display,
                        desc,
                        format!("({}:{})", file, line).dimmed()
                    );
                }
            }
        }

        if let Some(recs) = report["recommendations"].as_array() {
            if !recs.is_empty() {
                println!("\n  {}", "💡 RECOMMENDATIONS:".bright_cyan().bold());
                for r in recs.iter().take(10) {
                    println!("    {} {}", "→".blue(), r.as_str().unwrap_or(""));
                }
            }
        }

        println!(
            "\n{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );
    }

    pub async fn scan(&mut self, category: &str) -> Result<()> {
        println!(
            "\n{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );
        println!(
            "  {}",
            format!("🛡️  VORIA FULL SECURITY SCAN [{}]", category.to_uppercase())
                .blue()
                .bold()
        );
        println!(
            "{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );
        println!("  {} Scanning codebase...\n", "⏳".dimmed());

        let request = Request {
            command: "scan".to_string(),
            issue_id: None,
            repo_path: None,
            iteration: None,
            extra: serde_json::json!({
                "category": category
            }),
        };

        self.pm.send_request(&request).await?;
        let response = self.process_responses().await?;

        if response.status == "success" {
            if let Some(scan) = response.extra.get("data").and_then(|d| d.get("scan")) {
                let total = scan["total_tests"].as_u64().unwrap_or(0);
                let passed = scan["passed"].as_u64().unwrap_or(0);
                let failed = scan["failed"].as_u64().unwrap_or(0);
                let warnings = scan["warnings"].as_u64().unwrap_or(0);
                let avg_score = scan["avg_score"].as_f64().unwrap_or(0.0);

                println!(
                    "  {}",
                    "╔════════════════════════════════════════════════════════╗".blue()
                );
                println!(
                    "  {}  {:<18}: {}{}",
                    "║".blue(),
                    "Total Tests".blue().bold(),
                    total.to_string().white().bold(),
                    " ".repeat(35 - total.to_string().len()) + &"║".blue().to_string(),
                );
                println!(
                    "  {}  {:<18}: {}{}",
                    "║".blue(),
                    "Passed".green().bold(),
                    passed.to_string().green().bold(),
                    " ".repeat(35 - passed.to_string().len()) + &"║".blue().to_string(),
                );
                println!(
                    "  {}  {:<18}: {}{}",
                    "║".blue(),
                    "Failed".red().bold(),
                    failed.to_string().red().bold(),
                    " ".repeat(35 - failed.to_string().len()) + &"║".blue().to_string(),
                );
                println!(
                    "  {}  {:<18}: {}{}",
                    "║".blue(),
                    "Warnings".yellow().bold(),
                    warnings.to_string().yellow().bold(),
                    " ".repeat(35 - warnings.to_string().len()) + &"║".blue().to_string(),
                );

                let score_str = format!("{:.1}/100", avg_score);
                let score_disp = if avg_score >= 80.0 {
                    score_str.green().bold().to_string()
                } else if avg_score >= 50.0 {
                    score_str.yellow().bold().to_string()
                } else {
                    score_str.red().bold().to_string()
                };
                println!(
                    "  {}  {:<18}: {}{}",
                    "║".blue(),
                    "Average Score".blue().bold(),
                    score_disp,
                    " ".repeat(35 - format!("{:.1}/100", avg_score).len())
                        + &"║".blue().to_string(),
                );
                println!(
                    "  {}",
                    "╚════════════════════════════════════════════════════════╝".blue()
                );

                // Show findings
                if let Some(findings) = scan["findings"].as_array() {
                    if !findings.is_empty() {
                        println!("\n  {}", "⚠  FINDINGS:".yellow().bold());
                        for f in findings.iter().take(15) {
                            let severity = f["severity"].as_str().unwrap_or("low");
                            let desc = f["description"].as_str().unwrap_or("");
                            let test = f["test"].as_str().unwrap_or("");
                            let sev_display = match severity {
                                "high" | "critical" => format!("[{}]", severity.to_uppercase())
                                    .red()
                                    .bold()
                                    .to_string(),
                                "medium" => format!("[{}]", severity.to_uppercase())
                                    .yellow()
                                    .to_string(),
                                _ => format!("[{}]", severity.to_uppercase())
                                    .dimmed()
                                    .to_string(),
                            };
                            println!(
                                "    {} {} {}",
                                sev_display,
                                desc,
                                format!("({})", test).dimmed()
                            );
                        }
                    }
                }

                // Show recommendations
                if let Some(recs) = scan["recommendations"].as_array() {
                    if !recs.is_empty() {
                        println!("\n  {}", "💡 RECOMMENDATIONS:".bright_cyan().bold());
                        for r in recs.iter().take(10) {
                            println!("    {} {}", "→".blue(), r.as_str().unwrap_or(""));
                        }
                    }
                }

                println!(
                    "\n{}",
                    "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
                );
            } else {
                ui::print_success(&response.message);
            }
        } else {
            ui::print_error(&response.message);
        }

        self.pm.stop().await?;
        Ok(())
    }

    pub async fn diff(&mut self, ref_a: &str, ref_b: &str) -> Result<()> {
        println!(
            "\n{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );
        println!(
            "  {}",
            format!("🔀 SECURITY DIFF: {} → {}", ref_a, ref_b)
                .blue()
                .bold()
        );
        println!(
            "{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );

        let request = Request {
            command: "diff".to_string(),
            issue_id: None,
            repo_path: None,
            iteration: None,
            extra: serde_json::json!({
                "ref_a": ref_a,
                "ref_b": ref_b
            }),
        };

        self.pm.send_request(&request).await?;
        let response = self.process_responses().await?;

        if response.status == "success" {
            if let Some(diff) = response.extra.get("data").and_then(|d| d.get("diff")) {
                let total = diff["total_changed"].as_u64().unwrap_or(0);
                let risk_level = diff["risk_level"].as_str().unwrap_or("low");
                let risk_delta = diff["risk_delta"].as_u64().unwrap_or(0);

                let risk_display = match risk_level {
                    "critical" => "🔴 CRITICAL".red().bold().to_string(),
                    "elevated" => "🟡 ELEVATED".yellow().bold().to_string(),
                    _ => "🟢 LOW".green().bold().to_string(),
                };

                println!(
                    "\n  {:<20}: {}",
                    "Files Changed".blue().bold(),
                    total.to_string().white().bold()
                );
                println!("  {:<20}: {}", "Risk Level".blue().bold(), risk_display);
                println!(
                    "  {:<20}: {}",
                    "Risk Score".blue().bold(),
                    risk_delta.to_string().white()
                );

                if let Some(high) = diff["high_risk_files"].as_array() {
                    if !high.is_empty() {
                        println!(
                            "\n  {} {}",
                            "🔴 HIGH RISK FILES:".red().bold(),
                            format!("({})", high.len()).dimmed()
                        );
                        for f in high {
                            println!("    {} {}", "⚠".red(), f.as_str().unwrap_or("").red());
                        }
                    }
                }

                if let Some(med) = diff["medium_risk_files"].as_array() {
                    if !med.is_empty() {
                        println!(
                            "\n  {} {}",
                            "🟡 MEDIUM RISK FILES:".yellow().bold(),
                            format!("({})", med.len()).dimmed()
                        );
                        for f in med {
                            println!("    {} {}", "●".yellow(), f.as_str().unwrap_or("").yellow());
                        }
                    }
                }

                if let Some(low) = diff["low_risk_files"].as_array() {
                    if !low.is_empty() {
                        println!(
                            "\n  {} {}",
                            "🟢 LOW RISK FILES:".green().bold(),
                            format!("({})", low.len()).dimmed()
                        );
                        for f in low.iter().take(10) {
                            println!("    {} {}", "·".dimmed(), f.as_str().unwrap_or(""));
                        }
                        if low.len() > 10 {
                            println!("    {} ...and {} more", "·".dimmed(), low.len() - 10);
                        }
                    }
                }

                if let Some(rec) = diff["recommendation"].as_str() {
                    println!("\n  {}", "💡 RECOMMENDATION:".bright_cyan().bold());
                    println!("    {} {}", "→".blue(), rec);
                }
            } else {
                ui::print_success(&response.message);
            }
        } else {
            ui::print_error(&response.message);
        }

        println!(
            "\n{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );
        self.pm.stop().await?;
        Ok(())
    }

    pub async fn benchmark(&mut self, url: &str, requests: u32, concurrency: u32) -> Result<()> {
        println!(
            "\n{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );
        println!("  {}", format!("⚡ HTTP BENCHMARK: {}", url).blue().bold());
        println!(
            "  {}",
            format!("  {} requests, {} concurrency", requests, concurrency).dimmed()
        );
        println!(
            "{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );
        println!("  {} Benchmarking...\n", "⏳".dimmed());

        let request = Request {
            command: "benchmark".to_string(),
            issue_id: None,
            repo_path: None,
            iteration: None,
            extra: serde_json::json!({
                "url": url,
                "requests": requests,
                "concurrency": concurrency
            }),
        };

        self.pm.send_request(&request).await?;
        let response = self.process_responses().await?;

        if response.status == "success" {
            if let Some(bm) = response.extra.get("data").and_then(|d| d.get("benchmark")) {
                let rps = bm["rps"].as_f64().unwrap_or(0.0);
                let avg = bm["latency_avg_ms"].as_f64().unwrap_or(0.0);
                let p50 = bm["latency_p50_ms"].as_f64().unwrap_or(0.0);
                let p95 = bm["latency_p95_ms"].as_f64().unwrap_or(0.0);
                let p99 = bm["latency_p99_ms"].as_f64().unwrap_or(0.0);
                let min = bm["latency_min_ms"].as_f64().unwrap_or(0.0);
                let max = bm["latency_max_ms"].as_f64().unwrap_or(0.0);
                let successful = bm["successful"].as_u64().unwrap_or(0);
                let failed = bm["failed"].as_u64().unwrap_or(0);
                let total_time = bm["total_time_sec"].as_f64().unwrap_or(0.0);

                println!(
                    "  {}",
                    "╔═══════════════════════════════════════════╗".blue()
                );
                println!(
                    "  {}  {:<20}: {:<20} {}",
                    "║".blue(),
                    "Requests/sec".blue().bold(),
                    format!("{:.1}", rps).green().bold(),
                    "║".blue()
                );
                println!(
                    "  {}  {:<20}: {:<20} {}",
                    "║".blue(),
                    "Total Time".blue().bold(),
                    format!("{:.2}s", total_time).white(),
                    "║".blue()
                );
                println!(
                    "  {}  {:<20}: {:<20} {}",
                    "║".blue(),
                    "Successful".blue().bold(),
                    successful.to_string().green(),
                    "║".blue()
                );
                println!(
                    "  {}  {:<20}: {:<20} {}",
                    "║".blue(),
                    "Failed".blue().bold(),
                    failed.to_string().red(),
                    "║".blue()
                );
                println!(
                    "  {}",
                    "╠═══════════════════════════════════════════╣".blue()
                );
                println!(
                    "  {}  {}",
                    "║".blue(),
                    "  LATENCY DISTRIBUTION".blue().bold()
                );
                println!(
                    "  {}  {:<20}: {:<20} {}",
                    "║".blue(),
                    "Min".dimmed(),
                    format!("{:.2}ms", min).white(),
                    "║".blue()
                );
                println!(
                    "  {}  {:<20}: {:<20} {}",
                    "║".blue(),
                    "Average".dimmed(),
                    format!("{:.2}ms", avg).white(),
                    "║".blue()
                );
                println!(
                    "  {}  {:<20}: {:<20} {}",
                    "║".blue(),
                    "P50 (median)".blue().bold(),
                    format!("{:.2}ms", p50).green().bold(),
                    "║".blue()
                );
                println!(
                    "  {}  {:<20}: {:<20} {}",
                    "║".blue(),
                    "P95".yellow().bold(),
                    format!("{:.2}ms", p95).yellow().bold(),
                    "║".blue()
                );
                println!(
                    "  {}  {:<20}: {:<20} {}",
                    "║".blue(),
                    "P99".red().bold(),
                    format!("{:.2}ms", p99).red().bold(),
                    "║".blue()
                );
                println!(
                    "  {}  {:<20}: {:<20} {}",
                    "║".blue(),
                    "Max".dimmed(),
                    format!("{:.2}ms", max).white(),
                    "║".blue()
                );
                println!(
                    "  {}",
                    "╚═══════════════════════════════════════════╝".blue()
                );

                // Status codes
                if let Some(codes) = bm["status_codes"].as_object() {
                    println!("\n  {}", "  STATUS CODES:".blue().bold());
                    for (code, count) in codes {
                        let code_display = if code.starts_with('2') {
                            code.green().to_string()
                        } else if code.starts_with('3') {
                            code.cyan().to_string()
                        } else if code.starts_with('4') {
                            code.yellow().to_string()
                        } else {
                            code.red().to_string()
                        };
                        println!("    {} : {}", code_display, count);
                    }
                }
            } else {
                ui::print_success(&response.message);
            }
        } else {
            ui::print_error(&response.message);
        }

        println!(
            "\n{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );
        self.pm.stop().await?;
        Ok(())
    }

    pub async fn ci(&mut self, output: Option<String>) -> Result<()> {
        println!("{}", "  🏗️  Running CI security scan...".blue());

        let request = Request {
            command: "ci".to_string(),
            issue_id: None,
            repo_path: None,
            iteration: None,
            extra: serde_json::json!({}),
        };

        self.pm.send_request(&request).await?;
        let response = self.process_responses().await?;

        if response.status == "success" {
            if let Some(sarif) = response.extra.get("data").and_then(|d| d.get("sarif")) {
                let sarif_json = serde_json::to_string_pretty(sarif)?;

                if let Some(ref path) = output {
                    std::fs::write(path, &sarif_json)?;
                    println!(
                        "{}",
                        format!("  ✓ SARIF report written to: {}", path)
                            .green()
                            .bold()
                    );
                } else {
                    // Write to default path
                    let default_path = "voria-results.sarif";
                    std::fs::write(default_path, &sarif_json)?;
                    println!(
                        "{}",
                        format!("  ✓ SARIF report written to: {}", default_path)
                            .green()
                            .bold()
                    );
                }

                let count = response
                    .extra
                    .get("data")
                    .and_then(|d| d.get("findings_count"))
                    .and_then(|c| c.as_u64())
                    .unwrap_or(0);

                println!(
                    "{}",
                    format!("  📊 {} findings exported for GitHub Security tab", count).blue()
                );
                println!(
                    "{}",
                    "  💡 Upload with: gh sarif upload voria-results.sarif".bright_cyan()
                );
            } else {
                ui::print_success(&response.message);
            }
        } else {
            ui::print_error(&response.message);
        }

        self.pm.stop().await?;
        Ok(())
    }

    pub async fn watch(&mut self, test_ids: Vec<String>) -> Result<()> {
        println!(
            "\n{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );
        println!("  {}", "👁️  VORIA WATCH MODE".blue().bold());
        println!(
            "{}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".blue()
        );
        println!("  {} Monitoring for file changes...", "⏳".dimmed());
        println!(
            "  {} Tests: {}",
            "🧪".dimmed(),
            test_ids.join(", ").bright_cyan()
        );
        println!(
            "  {} Press {} to stop\n",
            "·".dimmed(),
            "Ctrl+C".yellow().bold()
        );

        // Initial setup via Python
        let request = Request {
            command: "watch".to_string(),
            issue_id: None,
            repo_path: None,
            iteration: None,
            extra: serde_json::json!({
                "test_ids": test_ids
            }),
        };

        self.pm.send_request(&request).await?;
        let response = self.process_responses().await?;

        if response.status == "success" {
            if let Some(watch_data) = response.extra.get("data").and_then(|d| d.get("watch")) {
                let files = watch_data["files_monitored"].as_u64().unwrap_or(0);
                println!(
                    "  {} {} files indexed and monitored",
                    "✓".green().bold(),
                    files.to_string().blue().bold()
                );
            }
            ui::print_success(&response.message);
        } else {
            ui::print_error(&response.message);
        }

        // Rust-side file watching loop
        let watch_path = std::env::current_dir()?;
        let mut snapshot = self.get_file_snapshot(&watch_path);
        println!(
            "  {} Watching {} files for changes...\n",
            "👁️".blue(),
            snapshot.len().to_string().blue().bold()
        );

        self.pm.stop().await?;

        loop {
            tokio::time::sleep(std::time::Duration::from_secs(2)).await;
            let new_snapshot = self.get_file_snapshot(&watch_path);

            let changed: Vec<String> = new_snapshot
                .iter()
                .filter(|(k, v)| snapshot.get(k.as_str()) != Some(*v))
                .map(|(k, _)| k.clone())
                .collect();

            if !changed.is_empty() {
                println!(
                    "\n  {} Detected {} file change(s):",
                    "🔄".blue().bold(),
                    changed.len().to_string().yellow()
                );
                for f in &changed {
                    println!("    {} {}", "→".blue(), f.bright_cyan());
                }
                println!("  {} Re-running tests...\n", "⏳".dimmed());

                // Re-run tests
                for test_id in &test_ids {
                    match Orchestrator::new(self.config.clone()).await {
                        Ok(mut orch) => {
                            let _ = orch.run_test(test_id).await;
                        }
                        Err(e) => {
                            eprintln!("  {} Failed to run test {}: {}", "✗".red(), test_id, e);
                        }
                    }
                }

                snapshot = new_snapshot;
            }
        }
    }

    fn get_file_snapshot(&self, path: &std::path::Path) -> std::collections::HashMap<String, u64> {
        use std::collections::HashMap;
        let mut snap = HashMap::new();
        let extensions = ["py", "js", "ts", "go", "rs", "java", "tsx", "jsx"];
        let excludes = [
            "node_modules",
            "target",
            ".git",
            "venv",
            "__pycache__",
            ".next",
            "dist",
        ];

        for entry in walkdir::WalkDir::new(path)
            .into_iter()
            .filter_map(|e| e.ok())
            .take(5000)
        {
            let p = entry.path();
            let p_str = p.to_string_lossy();
            if excludes.iter().any(|e| p_str.contains(e)) {
                continue;
            }
            if let Some(ext) = p.extension().and_then(|e| e.to_str()) {
                if extensions.contains(&ext) {
                    if let Ok(meta) = p.metadata() {
                        if let Ok(modified) = meta.modified() {
                            let secs = modified
                                .duration_since(std::time::UNIX_EPOCH)
                                .unwrap_or_default()
                                .as_secs();
                            snap.insert(p_str.to_string(), secs);
                        }
                    }
                }
            }
        }
        snap
    }

    pub async fn send_request_and_print_response(&mut self, request: &Request) -> Result<()> {
        self.pm.send_request(request).await?;
        let response = self.process_responses().await?;
        self.handle_response(&response).await?;
        self.pm.stop().await?;
        Ok(())
    }

    async fn handle_response(&self, response: &Response) -> Result<()> {
        match response.status.as_str() {
            "success" => {
                ui::print_success(&response.message);
                if let Some(ref logs) = response.logs {
                    eprintln!("{}", logs);
                }
            }
            "pending" => {
                if let Some(ref chunk) = response.chunk {
                    print!("{}", chunk.blue());
                    let _ = std::io::stdout().flush();
                } else {
                    ui::print_info(&response.message);
                }
            }
            "error" => {
                println!(); // Ensure new line after streaming
                ui::print_error(&response.message);
                if let Some(ref logs) = response.logs {
                    eprintln!("{}", logs);
                }
            }
            _ => {
                ui::print_info(&format!("Unknown status: {}", response.status));
            }
        }
        Ok(())
    }
}

fn textwrap(text: &str, width: usize) -> Vec<String> {
    let words: Vec<&str> = text.split_whitespace().collect();
    let mut lines = Vec::new();
    let mut current = String::new();
    for word in words {
        if current.len() + word.len() + 1 > width && !current.is_empty() {
            lines.push(current.clone());
            current.clear();
        }
        if !current.is_empty() {
            current.push(' ');
        }
        current.push_str(word);
    }
    if !current.is_empty() {
        lines.push(current);
    }
    if lines.is_empty() {
        lines.push(String::new());
    }
    lines
}
