use colored::Colorize;

pub fn print_info(msg: &str) {
    println!(" {}  {}", "ℹ".blue().bold(), msg.blue());
}

pub fn print_success(msg: &str) {
    println!(" {}  {}", "✓".green().bold(), msg);
}

pub fn print_error(msg: &str) {
    eprintln!(" {}  {}", "✗".red().bold(), msg.red());
}

#[allow(dead_code)]
pub fn print_warning(msg: &str) {
    println!(" {}  {}", "⚠".yellow().bold(), msg.yellow());
}

#[allow(dead_code)]
pub fn print_banner() {
    println!(
        "{}",
        "
  ╔══════════════════════════════════════════════════════╗
  ║                                                      ║
  ║   ██╗   ██╗ ██████╗ ██████╗ ██╗ █████╗               ║
  ║   ██║   ██║██╔═══██╗██╔══██╗██║██╔══██╗              ║
  ║   ██║   ██║██║   ██║██████╔╝██║███████║              ║
  ║   ╚██╗ ██╔╝██║   ██║██╔══██╗██║██╔══██║              ║
  ║    ╚████╔╝ ╚██████╔╝██║  ██║██║██║  ██║              ║
  ║     ╚═══╝   ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝              ║
  ║                                                      ║
  ║   AI-Powered Security & Reliability Engine  v0.0.5   ║
  ║                                                      ║
  ╚══════════════════════════════════════════════════════╝
"
        .blue()
        .bold()
    );
}
