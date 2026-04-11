# Contributors Guide

Thank you for being interested in contributing to Victory! This guide will help you get started.

## Quick Links

- **Issues**: https://github.com/Srizdebnath/Victory/issues
- **Discussions**: https://github.com/Srizdebnath/Victory/discussions
- **Contributing**: [CONTRIBUTING.md](./docs/CONTRIBUTING.md)
- **Code of Conduct**: [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- **Development Setup**: [DEVELOPMENT.md](./docs/DEVELOPMENT.md)

## Ways to Contribute

### 1. 🐛 Report Issues
Found a bug? Let us know!
- Check if it already exists
- Create a [bug report](https://github.com/Srizdebnath/Victory/issues/new?template=bug-report.yml)
- Include steps to reproduce

### 2. 💡 Suggest Features
Have an idea? We'd love to hear it!
- Check [existing features](https://github.com/Srizdebnath/Victory/issues?q=label:enhancement)
- Create a [feature request](https://github.com/Srizdebnath/Victory/issues/new?template=feature-request.yml)
- Explain the use case and benefits

### 3. 📝 Improve Documentation
Documentation helps everyone!
- Fix typos and clarify explanations
- Add examples and use cases
- Create guides or tutorials
- Translate documentation

**To contribute docs:**
1. Edit files in `/docs`
2. Preview locally
3. Submit a PR with changes

### 4. 💻 Write Code
Ready to code? Awesome!

**Good First Issues** for new contributors:
- [good-first-issue label](https://github.com/Srizdebnath/Victory/labels/good-first-issue)
- Start with these to get familiar with the codebase

**Areas we need help with:**
- [ ] LLM provider improvements
- [ ] GitHub integration features
- [ ] Test coverage expansion
- [ ] Performance optimization
- [ ] CLI enhancements
- [ ] Error handling

### 5. 🧪 Write Tests
Robust tests make Victory better!
- Unit tests for new functions
- Integration tests for features
- Edge case coverage
- Error scenario testing

### 6. 🎨 Improve UI/UX
Help make Victory more user-friendly!
- CLI output improvements
- Better error messages
- Help text enhancements
- Color scheme and formatting

### 7. 🌍 Translate
Help Victory reach more developers!
- Translate documentation
- Translate error messages
- Localize examples

### 8. 🔗 Community
Build our community!
- Share Victory with others
- Write blog posts or tutorials
- Speak about Victory at meetups
- Help answer questions

## Getting Started

### Prerequisites
- Git
- Node.js (v16+)
- Python (v3.9+)
- Rust (for CLI development)
- GitHub account

### Setup

1. **Fork the repository**
   - Click "Fork" on GitHub

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Victory.git
   cd Victory
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/Srizdebnath/Victory.git
   ```

4. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Install dependencies**
   ```bash
   # Rust CLI
   cd rust && cargo build && cd ..
   
   # Python engine
   cd python && pip install -e . && cd ..
   ```

6. **Make your changes**
   - Write code and tests
   - Follow coding standards
   - Update documentation

7. **Test your changes**
   ```bash
   # Rust
   cd rust && cargo test && cd ..
   
   # Python
   cd python && pytest && cd ..
   
   # Integration
   ./target/debug/victory plan 1
   ```

8. **Commit with conventional commits**
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve issue #123"
   git commit -m "docs: update README"
   ```

9. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Go to GitHub and create a Pull Request
   - Fill out the PR template

## Code Standards

### Rust
- Use `cargo fmt` for formatting
- Use `cargo clippy` for linting
- Write tests for new code
- Follow Rust naming conventions

### Python
- Use `black` for formatting
- Use `flake8` for linting
- Use `mypy` for type checking
- Follow PEP 8 guidelines

### Commit Messages
Follow conventional commits:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `test:` tests
- `refactor:` code cleanup
- `perf:` performance

Example:
```bash
git commit -m "feat: add support for Claude 4.6 model

- Implement claude_provider.py
- Add model discovery logic
- Update documentation
- Add integration tests

Fixes #123"
```

## PR Review Process

1. **Submit PR** with description and tests
2. **Automated checks** run (tests, linting)
3. **Maintainer reviews** code
4. **Address feedback** if needed
5. **Merge** when approved

## Recognition

Contributors are recognized:
- In README.md
- In release notes
- On the contributors page
- In community discussions

## Questions?

- **Documentation**: Check [docs/](./docs/)
- **Issues**: Search [existing issues](https://github.com/Srizdebnath/Victory/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Srizdebnath/Victory/discussions)
- **Email**: srizd449@gmail.com

## Code of Conduct

Please review our [Code of Conduct](./CODE_OF_CONDUCT.md). We're committed to providing a welcoming and inspiring community.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Victory! Happy coding! 🚀**

Need help getting started? Feel free to ask in the [discussions](https://github.com/Srizdebnath/Victory/discussions)!
