use anyhow::{anyhow, Result};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::process::Child as TokioChild;
use tokio::sync::Mutex;
use std::process::Stdio;
use std::sync::Arc;
use tracing::{debug, info};

/// NDJSON message types
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Request {
    pub command: String,
    pub issue_id: Option<u64>,
    pub repo_path: Option<String>,
    pub iteration: Option<u32>,
    #[serde(flatten)]
    pub extra: Value,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Response {
    pub status: String, // success, pending, error
    pub action: String, // apply_patch, run_tests, continue, stop
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub patch: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub logs: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub token_usage: Option<TokenUsage>,
    #[serde(flatten)]
    pub extra: Value,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TokenUsage {
    pub used: u32,
    pub max: u32,
    pub cost: f32,
}

pub struct ProcessManager {
    config: crate::config::Config,
    process: Arc<Mutex<Option<TokioChild>>>,
    stdin: Arc<Mutex<Option<tokio::process::ChildStdin>>>,
    reader: Arc<Mutex<Option<BufReader<tokio::process::ChildStdout>>>>,
}

impl ProcessManager {
    pub async fn new(config: crate::config::Config) -> Result<Self> {
        let manager = Self {
            config,
            process: Arc::new(Mutex::new(None)),
            stdin: Arc::new(Mutex::new(None)),
            reader: Arc::new(Mutex::new(None)),
        };
        manager.spawn_process().await?;
        Ok(manager)
    }

    async fn spawn_process(&self) -> Result<()> {
        info!(
            "Spawning Python engine: {} -m {}",
            self.config.python_path, self.config.engine_module
        );

        let mut child = tokio::process::Command::new(&self.config.python_path)
            .arg("-m")
            .arg(&self.config.engine_module)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit())
            .spawn()?;

        let stdin = child
            .stdin
            .take()
            .ok_or_else(|| anyhow!("Failed to open Python stdin"))?;
        let stdout = child
            .stdout
            .take()
            .ok_or_else(|| anyhow!("Failed to open Python stdout"))?;

        let reader = BufReader::new(stdout);

        *self.process.lock().await = Some(child);
        *self.stdin.lock().await = Some(stdin);
        *self.reader.lock().await = Some(reader);

        debug!("Python process started successfully");
        Ok(())
    }

    pub async fn send_request(&self, request: &Request) -> Result<()> {
        let json = serde_json::to_string(request)?;
        debug!("Sending request: {}", json);

        let mut stdin = self.stdin.lock().await;
        if let Some(ref mut child_stdin) = *stdin {
            child_stdin.write_all(json.as_bytes()).await?;
            child_stdin.write_all(b"\n").await?;
            child_stdin.flush().await?;
            debug!("Request flushed");
        } else {
            return Err(anyhow!("Python process stdin not available"));
        }

        Ok(())
    }

    pub async fn read_response(&self) -> Result<Response> {
        let mut reader = self.reader.lock().await;
        if let Some(ref mut buf_reader) = *reader {
            let mut line = String::new();
            let bytes_read = buf_reader.read_line(&mut line).await?;

            if bytes_read == 0 {
                return Err(anyhow!("Python process closed the connection"));
            }

            let response: Response = serde_json::from_str(line.trim())?;
            debug!("Received response: {:?}", response);
            Ok(response)
        } else {
            Err(anyhow!("Python process stdout not available"))
        }
    }

    pub async fn stop(&self) -> Result<()> {
        if let Some(mut child) = self.process.lock().await.take() {
            info!("Stopping Python process");
            child.kill().await?;
            debug!("Python process stopped");
        }
        Ok(())
    }
}
