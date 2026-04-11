#![allow(dead_code)]
use colored::Colorize;

pub fn print_info(msg: &str) {
    println!("{} {}", " ℹ ".on_blue().white().bold(), msg.blue());
}

pub fn print_success(msg: &str) {
    println!("{} {}", " ✓ ".on_green().white().bold(), msg.green());
}

pub fn print_error(msg: &str) {
    eprintln!("{} {}", " ✖ ".on_red().white().bold(), msg.red());
}

pub fn print_warning(msg: &str) {
    println!("{} {}", " ⚠ ".on_yellow().black().bold(), msg.yellow());
}

pub fn print_step(step: &str) {
    println!("\n{} {}", " ⚡ ".on_bright_blue().white().bold(), step.bright_blue().bold());
}

pub fn print_header(title: &str) {
    let line = "━".repeat(title.len() + 4);
    println!("\n{}", line.blue());
    println!("  {}", title.blue().bold());
    println!("{}", line.blue());
}
