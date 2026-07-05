with staged as (

    select * from "sentiment_data"."public"."stg_news_sentiment"

)

select
    news_source,
    sentiment_label,
    count(*) as article_count,
    round(avg(sentiment_polarity)::numeric, 3) as avg_polarity,
    round(avg(sentiment_subjectivity)::numeric, 3) as avg_subjectivity
from staged
group by 1, 2
order by 1, 2