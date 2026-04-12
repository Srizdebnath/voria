mod cli;
mod config;
mod ipc;
mod orchestrator;
mod ui;
mod analysis;

use anyhow::Result;
use clap::Parser;
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "voria")]
#[command(about = "AI-powered CLI tool for open source contributors", long_about = None)]
#[command(version = env!("CARGO_PKG_VERSION"))]
struct Args {
    #[command(subcommand)]
    command: Option<cli::Command>,

    /// Verbose logging
    #[arg(global = true, short, long)]
    verbose: bool,

    /// Configuration file path
    #[arg(global = true, short, long)]
    config: Option<PathBuf>,

    /// Show dependency graph and risk analysis
    #[arg(long)]
    graph: bool,
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

    if args.graph {
        let analyzer = analysis::CodeAnalyzer::new(std::env::current_dir()?);
        let result = analyzer.analyze().await?;
        analyzer.visualize_graph(&result);
        analyzer.display_risk_report(&result);
        return Ok(());
    }

    // Execute command
    if let Some(cmd) = args.command {
        cmd.execute(&config).await?;
    } else if !args.graph {
        // If no subcommand and no graph flag, show help
        use clap::CommandFactory;
        Args::command().print_help()?;
        println!();
    }

    Ok(())
}
