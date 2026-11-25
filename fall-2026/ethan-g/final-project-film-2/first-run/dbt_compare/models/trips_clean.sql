-- the clean 10,000-row sample
select * from read_parquet('{{ var("data_dir") }}/clean.parquet')
