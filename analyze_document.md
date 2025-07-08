ABSTRACT STEPS TO ANALYZE (applied to all features)

1. Upload product profile document (only once needed, can change, remove, add...)
2. Run Analyze
3. Check Analyze Progress
4. Get result

EXAMPLE

1. Product Profile

GET /product/{product_id}/profile/document/upload-url
To get upload document url


POST /product/{product_id}/profile/analyze
To run Analyze


GET /product/{product_id}/profile/analyze-progress
To get progress


GET /product/{product_id}/profile/analysis
To get analyze result


2. Competitive Analysis


POST /product/{product_id}/competitive-analysis/analyze
To run Analyze


GET /product/{product_id}/competitive-analysis/analyze-progress
To get progress


GET /product/{product_id}/competitive-analysis/result
GET /product/{product_id}/competitive-analysis/result/compare
...
To get analyze result



