use crate::config::Config;
use crate::ipc::{ProcessManager, Request, Response};
use crate::ui;
use anyhow::Result;
use tracing::info;

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
        info!("List issues request sent to Python engine");

        let response = self.pm.read_response().await?;
        info!("Response received: {:?}", response);

        self.handle_response(&response).await?;

        self.pm.stop().await?;
        Ok(())
    }

    pub async fn fix_issue(&mut self, owner: &str, repo: &str, issue_number: u64) -> Result<()> {
        ui::print_info(&format!("Fixing issue #{} from {}/{}", issue_number, owner, repo));

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
        info!("Fix issue request sent to Python engine");

        let response = self.pm.read_response().await?;
        info!("Response received: {:?}", response);

        self.handle_response(&response).await?;

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
        info!("Issue request sent to Python engine");

        let response = self.pm.read_response().await?;
        info!("Response received: {:?}", response);

        self.handle_response(&response).await?;

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
        info!("Apply request sent to Python engine");

        let response = self.pm.read_response().await?;
        info!("Response received: {:?}", response);

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
