# Tables Directory

For large or complex tables, you can write them in individual `.tex` files in this directory (e.g., `tables/dataset_stats.tex`) and include them in main section files using `\input{tables/dataset_stats.tex}`.

## Guidelines
- Always use the `booktabs` package (`\toprule`, `\midrule`, `\bottomrule`) for clean academic formatting.
- Avoid vertical lines (`|`) in tables for professional typesetting.
- Use `\caption{}` above the table.
