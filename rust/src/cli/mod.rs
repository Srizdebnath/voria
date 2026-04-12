use crate::config::Config;
use crate::orchestrator::Orchestrator;
use anyhow::Result;
use clap::Subcommand;
use std::io::{self, Write};

#[derive(Subcommand)]
pub enum Command {
    /// Setup Modal API configuration
    SetupModal {
        /// Modal token
        #[arg(value_name = "TOKEN")]
        token: Option<String>,
    },
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
}

impl Command {
    pub async fn execute(&self, config: &Config) -> Result<()> {
        match self {
            Command::SetupModal { token } => self.handle_setup_modal(token.clone(), config).await,
            Command::SetGithubToken => self.handle_set_github_token(config).await,
            Command::ListIssues { repo } => self.handle_list_issues(repo.clone(), config).await,
            Command::Fix { issue_number, repo } => {
                self.handle_fix(*issue_number, repo.clone(), config).await
            }
            Command::Plan { issue_id } => self.handle_plan(*issue_id, config).await,
            Command::Issue { issue_id } => self.handle_issue(*issue_id, config).await,
            Command::Apply { plan } => self.handle_apply(plan, config).await,
        }
    }

    async fn handle_setup_modal(&self, token: Option<String>, config: &Config) -> Result<()> {
        let modal_token = if let Some(t) = token {
            t
        } else {
            print!("🔑 Enter your Modal API token (get it from https://modal.com): ");
            io::stdout().flush()?;
            let mut token = String::new();
            io::stdin().read_line(&mut token)?;
            token.trim().to_string()
        };

        if modal_token.is_empty() {
            eprintln!("❌ Modal token cannot be empty");
            return Ok(());
        }

        let mut new_config = config.clone();
        new_config.modal_token = Some(modal_token.clone());
        new_config.llm_provider = Some("modal".to_string());
        new_config.save_global()?;

        println!("✅ Modal API token saved successfully!");
        Ok(())
    }

    async fn handle_set_github_token(&self, config: &Config) -> Result<()> {
        print!("🔑 Enter your GitHub Personal Access Token: ");
        io::stdout().flush()?;
        let mut token = String::new();
        io::stdin().read_line(&mut token)?;
        let github_token = token.trim().to_string();

        let mut new_config = config.clone();
        new_config.github_token = Some(github_token);
        new_config.save_global()?;

        println!("✅ GitHub token saved successfully!");
        Ok(())
    }

    async fn handle_list_issues(&self, repo: Option<String>, config: &Config) -> Result<()> {
        if config.github_token.is_none() {
            eprintln!("❌ GitHub token not configured. Run: voria set-github-token");
            return Ok(());
        }

        let repo_url = if let Some(r) = repo {
            r
        } else {
            print!("📦 Enter repository URL or owner/repo: ");
            io::stdout().flush()?;
            let mut input = String::new();
            io::stdin().read_line(&mut input)?;
            input.trim().to_string()
        };

        println!("📋 Fetching issues from: {}", repo_url);

        // Parse repo URL to get owner and repo name
        let (owner, repo_name) = self.parse_repo_url(&repo_url)?;

        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        orchestrator.list_issues(&owner, &repo_name).await?;

        Ok(())
    }

    async fn handle_fix(
        &self,
        issue_number: u64,
        repo: Option<String>,
        config: &Config,
    ) -> Result<()> {
        if config.github_token.is_none() {
            eprintln!("❌ GitHub token not configured. Run: voria set-github-token");
            return Ok(());
        }

        if config.modal_token.is_none() && config.llm_api_key.is_none() {
            eprintln!("❌ LLM not configured. Run: voria setup-modal <token>");
            return Ok(());
        }

        let repo_url = if let Some(r) = repo {
            r
        } else {
            print!("📦 Enter repository URL or owner/repo: ");
            io::stdout().flush()?;
            let mut input = String::new();
            io::stdin().read_line(&mut input)?;
            input.trim().to_string()
        };

        let (owner, repo_name) = self.parse_repo_url(&repo_url)?;

        println!(
            "🔧 Fixing issue #{} from {}/{}",
            issue_number, owner, repo_name
        );

        let mut orchestrator = Orchestrator::new(config.clone()).await?;
        orchestrator
            .fix_issue(&owner, &repo_name, issue_number)
            .await?;

        Ok(())
    }

    fn parse_repo_url(&self, url: &str) -> Result<(String, String)> {
        let url = url.trim();

        // Handle owner/repo format
        if !url.contains('/') || url.starts_with("https://") || url.starts_with("http://") {
            // Parse GitHub URL
            let parts: Vec<&str> = url.split('/').collect();
            if parts.len() >= 2 {
                let owner = parts[parts.len() - 2].to_string();
                let repo = parts[parts.len() - 1].trim_end_matches(".git").to_string();
                Ok((owner, repo))
            } else {
                anyhow::bail!("Invalid repository URL format")
            }
        } else {
            // owner/repo format
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
}
