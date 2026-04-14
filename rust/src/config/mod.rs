use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Clone, Debug, Serialize, Deserialize)]
#[allow(dead_code)]
pub struct Config {
    #[serde(default = "default_python_path")]
    pub python_path: String,
    #[serde(default = "default_engine_module")]
    pub engine_module: String,
    #[serde(default = "default_process_timeout")]
    pub process_timeout: u64,
    #[serde(default = "default_max_retries")]
    pub max_retries: u32,
    #[serde(default)]
    pub github_token: Option<String>,
    #[serde(default)]
    pub modal_token: Option<String>,
    #[serde(default)]
    pub llm_provider: Option<String>,
    #[serde(default)]
    pub llm_api_key: Option<String>,
    #[serde(default)]
    pub llm_model: Option<String>,
    #[serde(default = "default_daily_budget")]
    pub daily_budget: Option<f64>,
    #[serde(default)]
    pub test_framework: Option<String>,
}

fn default_python_path() -> String { "python3".to_string() }
fn default_engine_module() -> String { "voria.engine".to_string() }
fn default_process_timeout() -> u64 { 30 }
fn default_max_retries() -> u32 { 1 }
fn default_daily_budget() -> Option<f64> { Some(10.0) }

impl Default for Config {
    fn default() -> Self {
        Self {
            python_path: "python3".to_string(),
            engine_module: "voria.engine".to_string(),
            process_timeout: 30,
            max_retries: 1,
            github_token: None,
            modal_token: None,
            llm_provider: None,
            llm_api_key: None,
            llm_model: None,
            daily_budget: Some(10.0),
            test_framework: None,
        }
    }
}

#[allow(dead_code)]
impl Config {
    pub fn load(path: PathBuf) -> Result<Self> {
        if path.exists() {
            let content = std::fs::read_to_string(&path)?;
            // Only support JSON for now
            Ok(serde_json::from_str(&content)?)
        } else {
            Ok(Self::default())
        }
    }

    pub fn save(&self, path: PathBuf) -> Result<()> {
        let content = serde_json::to_string_pretty(self)?;
        std::fs::write(path, content)?;
        Ok(())
    }

    pub fn load_global() -> Result<Self> {
        let path = Self::global_config_path()?;
        Self::load(path)
    }

    pub fn save_global(&self) -> Result<()> {
        let path = Self::global_config_path()?;
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        self.save(path)
    }

    fn global_config_path() -> Result<PathBuf> {
        let home = std::env::var("HOME").map(PathBuf::from)?;
        Ok(home.join(".voria").join("config.json"))
    }
}
