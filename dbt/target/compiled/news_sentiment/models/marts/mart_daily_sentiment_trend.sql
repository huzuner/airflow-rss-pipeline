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