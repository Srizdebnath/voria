use anyhow::Result;
use clap::Subcommand;
use crate::config::Config;
use crate::orchestrator::Orchestrator;

#[derive(Subcommand)]
pub enum Command {
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
            Command::Plan { issue_id } => {
                self.handle_plan(*issue_id, config).await
            }
            Command::Issue { issue_id } => {
                self.handle_issue(*issue_id, config).await
            }
            Command::Apply { plan } => {
                self.handle_apply(plan, config).await
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
