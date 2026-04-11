use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Clone, Debug, Serialize, Deserialize)]
#[allow(dead_code)]
pub struct Config {
    pub python_path: String,
    pub engine_module: String,
    pub process_timeout: u64,
    pub max_retries: u32,
    pub github_token: Option<String>,
    pub modal_token: Option<String>,
    pub llm_provider: Option<String>,
    pub llm_api_key: Option<String>,
    pub llm_model: Option<String>,
    pub daily_budget: Option<f64>,
    pub test_framework: Option<String>,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            python_path: "python3".to_string(),
            engine_module: "victory.engine".to_string(),
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
        Ok(home.join(".victory").join("config.json"))
    }
}
