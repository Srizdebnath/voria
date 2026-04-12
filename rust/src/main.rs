mod cli;
mod config;
mod ipc;
mod orchestrator;
mod ui;

use anyhow::Result;
use clap::Parser;
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "voria")]
#[command(about = "AI-powered CLI tool for open source contributors", long_about = None)]
#[command(version = env!("CARGO_PKG_VERSION"))]
struct Args {
    #[command(subcommand)]
    command: cli::Command,

    /// Verbose logging
    #[arg(global = true, short, long)]
    verbose: bool,

    /// Configuration file path
    #[arg(global = true, short, long)]
    config: Option<PathBuf>,
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();

    // Initialize logging
    let log_level = if args.verbose { "debug" } else { "info" };
    let env_filter = tracing_subscriber::EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new(log_level));

    tracing_subscriber::fmt().with_env_filter(env_filter).init();

    // Load config if provided
    let config = if let Some(config_path) = args.config {
        config::Config::load(config_path)?
    } else {
        config::Config::default()
    };

    // Execute command
    args.command.execute(&config).await
}
