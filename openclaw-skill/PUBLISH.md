# Publishing to ClawHub

This guide explains how to publish the USCIS Case Checker skill to [ClawHub](https://clawhub.ai/).

## Prerequisites

1. **ClawHub CLI installed:**
   ```bash
   # Install ClawHub CLI (example command)
   npm install -g @clawhub/cli
   # or
   pip install clawhub-cli
   ```

2. **ClawHub account:**
   - Sign up at https://clawhub.ai/
   - Verify your email
   - Get your API key from account settings

## Publishing Steps

### 1. Login to ClawHub

```bash
clawhub login
# Enter your API key when prompted
```

### 2. Navigate to the skill directory

```bash
cd openclaw-skill
```

### 3. Validate the skill

```bash
clawhub validate
```

This will check:
- `clawhub.json` syntax
- Required fields
- Entry point exists
- No missing dependencies

### 4. Test locally (optional but recommended)

```bash
# Install locally
clawhub install --local

# Test commands
clawhub run uscis-setup IOE1234567890
```

### 5. Publish to ClawHub

```bash
clawhub publish
```

This will:
- Upload the skill to ClawHub
- Make it available for installation
- Create a version entry

### 6. Verify publication

```bash
# Search for your skill
clawhub search uscis-case-checker

# View details
clawhub info uscis-case-checker
```

## Updating the Skill

When you release a new version:

1. Update version in `clawhub.json`:
   ```json
   {
     "version": "1.1.0"
   }
   ```

2. Update `CHANGELOG.md` with new features/fixes

3. Republish:
   ```bash
   clawhub publish
   ```

## Publishing Checklist

Before publishing, ensure:

- [ ] `clawhub.json` is valid and complete
- [ ] All commands are documented
- [ ] `skill.py` is executable
- [ ] README is clear and helpful
- [ ] Version is incremented appropriately
- [ ] No sensitive data in files
- [ ] License file exists
- [ ] Tested on target platforms

## Troubleshooting

### "Invalid manifest"
- Check JSON syntax in `clawhub.json`
- Ensure all required fields are present
- Validate with: `clawhub validate`

### "Entry point not found"
- Verify `skill.py` exists and is executable
- Check `entry_point` in `clawhub.json` matches filename

### "Permission denied"
- Make skill.py executable: `chmod +x skill.py`

### "Already published"
- Increment version number before republishing

## Alternative: Manual Upload

If CLI doesn't work, you can manually upload:

1. Go to https://clawhub.ai/publish
2. Fill in the skill details
3. Upload a ZIP file containing:
   - `skill.py`
   - `clawhub.json`
   - `README.md`
   - Any other required files
4. Submit for review

## Getting Help

- ClawHub Documentation: https://docs.clawhub.ai
- Community Forum: https://community.clawhub.ai
- GitHub Issues: https://github.com/GustavoZiaugra/uscis-case-checker/issues

## Post-Publication

After publishing:

1. **Update your GitHub README** with installation instructions:
   ```markdown
   ### Install via ClawHub
   
   ```bash
   clawhub install uscis-case-checker
   ```
   ```

2. **Share on social media** - Let the immigration community know!

3. **Monitor issues** - Check ClawHub reviews and GitHub issues

4. **Keep updated** - Regularly update the skill with improvements

## Tags and Categories

Make sure to use relevant tags in `clawhub.json`:
- `automation` - Core category
- `uscis` - Specific service
- `immigration` - Domain
- `notifications` - Feature
- `docker` - Technology

This helps users find your skill when searching.
