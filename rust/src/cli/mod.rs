use crate::config::Config;
use crate::orchestrator::Orchestrator;
use anyhow::Result;
use clap::Subcommand;
use colored::Colorize;
use std::io::{self, Write};

#[derive(Subcommand)]
pub enum Command {
    /// Setup Modal API configuration
    SetupModal {
        /// Modal token
        #[arg(value_name = "TOKEN")]
        token: Option<String>,
    },
    /// Initialize voria configuration interactively
    Init,
    /// Alias for init
    Setup,
    /// Set GitHub Personal Access Token
    SetGithubToken,
    /// List issues from a GitHub repository
    ListIssues {
        /// GitHub repository URL or owner/repo format
        #[arg(value_name = "REPO")]
        repo: Option<String>,
    },
    /// Fix a specific GitHub issue
    Fix {
        /// Issue number to fix
        #[arg(value_name = "ISSUE_NUMBER")]
        issue_number: u64,
        /// GitHub repository URL or owner/repo format
        #[arg(value_name = "REPO")]
        repo: Option<String>,
        /// Auto-apply the generated patch and run tests
        #[arg(long)]
        auto: bool,
    },
    /// Plan how to fix an issue
    Plan {
        /// Issue ID
        #[arg(value_name = "ISSUE_ID")]
        issue_id: u64,
    },
    /// Run full agent loop on an issue
    Issue {
        /// Issue ID
        #[arg(value_name = "ISSUE_ID")]
        issue_id: u64,
    },
    /// Apply an existing plan
    Apply {
        /// Plan ID or path
        #[arg(value_name = "PLAN")]
        plan: String,
    },
    /// Run a specific codebase test (security, performance, etc)
    Test {
        /// Test name or ID
        #[arg(value_name = "NAME")]
        name: Option<String>,
        /// List all available tests
        #[arg(long, short = 'l')]
        list: bool,
    },
    /// Full security scan — runs all tests in parallel and generates a report
    Scan {
        /// Category filter: security, production, performance, stress, quality, all
        #[arg(long, short = 'c', default_value = "all")]
        category: String,
    },
    /// Compare security posture between two git commits/branches
    Diff {
        /// First ref (default: HEAD~1)
        #[arg(value_name = "REF_A", default_value = "HEAD~1")]
        ref_a: String,
        /// Second ref (default: HEAD)
        #[arg(value_name = "REF_B", default_value = "HEAD")]
        ref_b: String,
    },
    /// HTTP benchmark a target URL — measure p50/p95/p99 latencies
    Benchmark {
        /// Target URL to benchmark
        #[arg(value_name = "URL")]
        url: String,
        /// Number of requests
        #[arg(long, short = 'n', default_value = "100")]
        requests: u32,
        /// Concurrency level
        #[arg(long, short = 'j', default_value = "10")]
        concurrency: u32,
    },
    /// CI/CD integration — output SARIF for GitHub Security tab
    Ci {
        /// Output file path for SARIF JSON
        #[arg(long, short = 'o')]
        output: Option<String>,
    },
    /// Watch mode — monitor files and re-run tests on changes
    Watch {
        /// Comma-separated list of test IDs to run
        #[arg(
            long,
            short = 't',
            default_value = "hardcoded_secrets,xss,sql_injection"
        )]
        tests: String,
    },
}

impl Command {
    pub async fn execute(&self, config: &Config) -> Result<()> {
        match self {
            Command::SetupModal { token } => self.handle_setup_modal(token.clone(), config).await,
            Command::Init | Command::Setup => self.handle_setup(config).await,
            Command::SetGithubToken => self.handle_set_github_token(config).await,
            Command::ListIssues { repo } => self.handle_list_issues(repo.clone(), config).await,
            Command::Fix {
                issue_number,
                repo,
                auto,
            } => {
                self.handle_fix(*issue_number, repo.clone(), *auto, config)
                    .await
            }
            Command::Plan { issue_id } => self.handle_plan(*issue_id, config).await,
            Command::Issue { issue_id } => self.handle_issue(*issue_id, config).await,
            Command::Apply { plan } => self.handle_apply(plan, config).await,
            Command::Test { name, list } => self.handle_test(name.clone(), *list, config).await,
            Command::Scan { category } => self.handle_scan(category, config).await,
            Command::Diff { ref_a, ref_b } => self.handle_diff(ref_a, ref_b, config).await,
            Command::Benchmark {
                url,
                requests,
                concurrency,
            } => {
                self.handle_benchmark(url, *requests, *concurrency, config)
                    .await
            }
            Command::Ci { output } => self.handle_ci(output.clone(), config).await,
            Command::Watch { tests } => self.handle_watch(tests, config).await,
        }
    }

    async fn handle_setup_modal(&self, token: Option<String>, config: &Config) -> Result<()> {
        let modal_token = if let Some(t) = token {
            t
        } else {
            print!("{}", "  🔑 Enter your Modal API token: ".blue());
            io::stdout().flush()?;
            let mut token = String::new();
            io::stdin().read_line(&mut token)?;
            token.trim().to_string()
        };

        if modal_token.is_empty() {
            eprintln!("{}", "  ✗ Modal token cannot be empty".red());
            return Ok(());
        }

        let mut new_config = config.clone();
        new_config.modal_token = Some(modal_token.clone());
        new_config.llm_provider = Some("modal".to_string());
        new_config.save_global()?;

        println!(
            "{}",
            "  ✓ Modal API token saved successfully!".blue().bold()
        );
        Ok(())
    }

    async fn handle_setup(&self, config: &Config) -> Result<()> {
        let mut orchestrator = Orchestrator::new(config.clone()).await?;

        let request = crate::ipc::Request {
            command: "config".to_string(),
            issue_id: None,
            repo_path: None,
            iteration: None,
            extra: serde_json::json!({
                "action": "init"
            }),
        };

        orchestrator.send_request_and_print_response(&request).await
    }

    async fn handle_set_github_token(&self, config: &Config) -> Result<()> {
        print!(
            "{}",
            "  🔑 Enter your GitHub Personal Access Token: ".blue()
        );
        io::stdout().flush()?;
        let mut token = String::new();
        io::stdin().read_line(&mut token)?;
        let github_token = token.trim().to_string();

        let mut new_config = config.clone();
        new_config.github_token = Some(github_token);
        new_config.save_global()?;

        println!("{}", "  ✓ GitHub token saved successfully!".blue().bold());
        Ok(())
    }

    async fn handle_list_issues(&self, repo: Option<String>, config: &Config) -> Result<()> {
        if config.github_token.is_none() {
            eprintln!(
                "{}",
                "  ✗ GitHub token not configured. Run: voria set-github-token".red()
            );
            return Ok(());
        }

        let repo_url = if let Some(r) = repo {
            r
        } else {
            print!("{}", "  📦 Enter repository URL or owner/repo: ".blue());
            io::stdout().flush()?;
            let mut input = String::new();
            io::stdin().read_line(&mut input)?;
            input.trim().to_string()
        };

        println!(
            "{}",
            format!("  📋 Fetching issues from: {}", repo_url).blue()
        );
        let (owner, repo_name) = self.parse_repo_url(&repo_url)?;
        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        orchestrator.list_issues(&owner, &repo_name).await?;
        Ok(())
    }

    async fn handle_fix(
        &self,
        issue_number: u64,
        repo: Option<String>,
        auto: bool,
        config: &Config,
    ) -> Result<()> {
        if config.github_token.is_none() {
            eprintln!(
                "{}",
                "  ✗ GitHub token not configured. Run: voria set-github-token".red()
            );
            return Ok(());
        }

        if config.modal_token.is_none() && config.llm_api_key.is_none() {
            eprintln!(
                "{}",
                "  ✗ LLM not configured. Run: voria setup-modal <token>".red()
            );
            return Ok(());
        }

        let repo_url = if let Some(r) = repo {
            r
        } else {
            print!("{}", "  📦 Enter repository URL or owner/repo: ".blue());
            io::stdout().flush()?;
            let mut input = String::new();
            io::stdin().read_line(&mut input)?;
            input.trim().to_string()
        };

        let (owner, repo_name) = self.parse_repo_url(&repo_url)?;

        if auto {
            println!(
                "{}",
                format!(
                    "  🤖 Auto-fixing issue #{} from {}/{}",
                    issue_number, owner, repo_name
                )
                .blue()
                .bold()
            );
        } else {
            println!(
                "{}",
                format!(
                    "  🔧 Fixing issue #{} from {}/{}",
                    issue_number, owner, repo_name
                )
                .blue()
            );
        }

        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        orchestrator
            .fix_issue(&owner, &repo_name, issue_number)
            .await?;

        if auto {
            println!(
                "{}",
                "  ⚡ Auto mode: applying patch and running tests...".blue()
            );
            // The fix handler in Python already applies the patch
            // Run a quick test suite afterwards
            orchestrator = Orchestrator::new(config.clone()).await?;
            orchestrator.run_test("hardcoded_secrets").await?;
        }

        Ok(())
    }

    fn parse_repo_url(&self, url: &str) -> Result<(String, String)> {
        let url = url.trim();

        // Handle owner/repo format
        if !url.contains('/') || url.starts_with("https://") || url.starts_with("http://") {
            let parts: Vec<&str> = url.split('/').collect();
            if parts.len() >= 2 {
                let owner = parts[parts.len() - 2].to_string();
                let repo = parts[parts.len() - 1].trim_end_matches(".git").to_string();
                Ok((owner, repo))
            } else {
                anyhow::bail!("Invalid repository URL format")
            }
        } else {
            let parts: Vec<&str> = url.split('/').collect();
            if parts.len() == 2 {
                Ok((parts[0].to_string(), parts[1].to_string()))
            } else {
                anyhow::bail!("Invalid repository format. Use owner/repo or full GitHub URL")
            }
        }
    }

    async fn handle_plan(&self, issue_id: u64, config: &Config) -> Result<()> {
        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        orchestrator.plan(issue_id).await
    }

    async fn handle_issue(&self, issue_id: u64, config: &Config) -> Result<()> {
        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        orchestrator.issue_loop(issue_id).await
    }

    async fn handle_apply(&self, plan: &str, config: &Config) -> Result<()> {
        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        orchestrator.apply(plan).await
    }

    async fn handle_test(&self, name: Option<String>, list: bool, config: &Config) -> Result<()> {
        let mut orchestrator = Orchestrator::new(config.clone()).await?;

        if list {
            orchestrator.list_tests().await?;
        } else if let Some(n) = name {
            orchestrator.run_test(&n).await?;
        } else {
            orchestrator.list_tests().await?;
        }

        Ok(())
    }

    async fn handle_scan(&self, category: &str, config: &Config) -> Result<()> {
        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        orchestrator.scan(category).await
    }

    async fn handle_diff(&self, ref_a: &str, ref_b: &str, config: &Config) -> Result<()> {
        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        orchestrator.diff(ref_a, ref_b).await
    }

    async fn handle_benchmark(
        &self,
        url: &str,
        requests: u32,
        concurrency: u32,
        config: &Config,
    ) -> Result<()> {
        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        orchestrator.benchmark(url, requests, concurrency).await
    }

    async fn handle_ci(&self, output: Option<String>, config: &Config) -> Result<()> {
        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        orchestrator.ci(output).await
    }

    async fn handle_watch(&self, tests: &str, config: &Config) -> Result<()> {
        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        let test_ids: Vec<String> = tests.split(',').map(|s| s.trim().to_string()).collect();
        orchestrator.watch(test_ids).await
    }
}
