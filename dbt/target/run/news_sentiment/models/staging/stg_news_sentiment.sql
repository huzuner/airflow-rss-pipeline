
  create view "sentiment_data"."public"."stg_news_sentiment__dbt_tmp"
    
    
  as (
    with source as (

    select * from "sentiment_data"."public"."news_sentiment"

)

select
    id,
    source as news_source,
    title,
    link,
    published_at,
    sentiment_polarity,
    sentiment_subjectivity,
    sentiment_label,
    fetched_at,
    date_trunc('day', fetched_at) as fetched_date
from source
  );