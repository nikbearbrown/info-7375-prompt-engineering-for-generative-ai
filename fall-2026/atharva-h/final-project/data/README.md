# data/

Put the source workbook here, or anywhere else; the loader takes a path. Nothing in this folder is committed except this file.

```bash
curl -L -o data/LCA_Disclosure_Data_FY2026_Q3.xlsx "https://www.dol.gov//media/LCA_Disclosure_Data_FY2026_Q3.xlsx"
shasum -a 256 data/LCA_Disclosure_Data_FY2026_Q3.xlsx
# expected: f8ca8448a528671f784d3692923775a13741c99caec2816b2fe30c8885bd28b3  (251,850,891 bytes)
python3 -m sponsorsql load data/LCA_Disclosure_Data_FY2026_Q3.xlsx data/fy2026q3.sqlite
```

The DOL replaces this file when it publishes a new quarter. If the download's checksum differs, the loader stops. Don't edit the expected checksum to make it pass: a new file needs a new answer key and a new freeze.
