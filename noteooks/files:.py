# coding: utf-8
import unibox as ub
import pandas as pd

uris = ["s3://dataset-pixiv/sagemaker/20240228_half_pixiv_optmize_workflow/0.todo.parquet",
        "s3://dataset-pixiv/sagemaker/20240228_half_pixiv_optmize_workflow/1.todo.parquet",
        "s3://dataset-pixiv/sagemaker/20240228_half_pixiv_optmize_workflow/2.todo.parquet",]

result_df = pd.concat(ub.concurrent_loads(uris))
ub.peeks(result_df)
import pandas as pd

uris = ["s3://dataset-pixiv/sagemaker/20240228_half_pixiv_optmize_workflow/0.todo.parquet",
        "s3://dataset-pixiv/sagemaker/20240228_half_pixiv_optmize_workflow/1.todo.parquet",
        "s3://dataset-pixiv/sagemaker/20240228_half_pixiv_optmize_workflow/2.todo.parquet",]

result_df = pd.concat(ub.concurrent_loads(uris))
ub.peeks(result_df)
