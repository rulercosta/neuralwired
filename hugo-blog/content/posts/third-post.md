      - name: Checkout
        uses: actions/checkout@v3
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
          extended: true
      - name: Build
        run: hugo --minify
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

## Configuring baseURL

Make sure your `config.toml` has the correct baseURL:

```toml
baseURL = "https://username.github.io/" # Replace with your actual URL
```

## Pushing Your Changes

After setting up the workflow, push your changes to GitHub:

```bash
git add .
git commit -m "Set up GitHub Pages deployment"
git push origin main
```

## Configuring GitHub Pages

In your repository settings, navigate to the "Pages" section and configure the source to deploy from the `gh-pages` branch that the GitHub Action creates.

## Using a Custom Domain (Optional)

If you want to use a custom domain:

1. Add a CNAME file to your `static` directory with your domain name
2. Update your DNS settings with your domain provider
3. Configure the custom domain in your GitHub Pages settings

## Conclusion

With GitHub Actions handling the build and deployment process, publishing updates to your Hugo site is as simple as committing changes to your repository. This workflow allows you to focus on creating content rather than managing deployment processes.
