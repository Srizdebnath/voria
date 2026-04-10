use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Config {
    /// Python executable path
    pub python_path: String,
    /// Python engine module path
    pub engine_module: String,
    /// Process timeout in seconds
    pub process_timeout: u64,
    /// Max retries for failed commands
    pub max_retries: u32,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            python_path: "python3".to_string(),
            engine_module: "victory.engine".to_string(),
            process_timeout: 30,
            max_retries: 1,
        }
    }
}

impl Config {
    pub fn load(_path: PathBuf) -> Result<Self> {
        // TODO: Load from YAML/TOML config file
        Ok(Self::default())
    }
}
