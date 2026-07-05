
  
    

  create  table "sentiment_data"."public"."mart_daily_sentiment_trend__dbt_tmp"
  
  
    as
  
  (
    with staged as (

    select * from "sentiment_data"."public"."stg_news_sentiment"

)

select
    fetched_date,
    news_source,
    sentiment_label,
    count(*) as article_count
from staged
group by 1, 2, 3
order by 1, 2, 3
  );
  