-- the copy with planted defects
select * from read_parquet('{{ var("data_dir") }}/broken.parquet')
