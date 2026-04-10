use crate::config::Config;
use crate::ipc::{ProcessManager, Request, Response};
use crate::ui;
use anyhow::Result;
use tracing::info;

pub struct Orchestrator {
    config: Config,
    pm: ProcessManager,
}

impl Orchestrator {
    pub async fn new(config: Config) -> Result<Self> {
        let pm = ProcessManager::new(config.clone()).await?;
        Ok(Self { config, pm })
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
        info!("Request sent to Python engine");

        let response = self.pm.read_response().await?;
        info!("Response received: {:?}", response);

        self.handle_response(&response).await?;

        self.pm.stop().await?;
        Ok(())
    }

    pub async fn issue_loop(&mut self, issue_id: u64) -> Result<()> {
        ui::print_info(&format!("Starting issue loop for #{}", issue_id));
        // TODO: Implement full agent loop
        Ok(())
    }

    pub async fn apply(&mut self, plan: &str) -> Result<()> {
        ui::print_info(&format!("Applying plan: {}", plan));
        // TODO: Implement apply logic
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
                ui::print_info(&response.message);
            }
            "error" => {
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
