R=/root/floor-v5-verify/repoC/independent/y131-floor-cert-freeze-v2-20261110/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
grep -E '^[A-Z_]+\|id=(127|139)\|' $R | tr '|' '\n' | grep -E '^(windows|open_checker|statement|namespace|build)=' | fold -w 400
