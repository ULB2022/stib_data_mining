from sqlalchemy import create_engine
import pandas as pd
from datetime import timedelta, datetime
import calendar


DB = "dm"
engine = create_engine(f"postgresql://localhost:5432/{DB}")


sql = 'select * from "gtfs3Sept_calendar"'
df = pd.read_sql(sql, engine)
data = []


for ind in df.index:
    start_date = df["start_date"][ind]
    end_date = df["end_date"][ind]
    while start_date <= end_date:
        date_time_obj = datetime.strptime(str(start_date), "%Y%m%d").date()
        # print(date_time_obj)
        day = calendar.day_name[date_time_obj.weekday()].lower()
        if df[day][ind] == 1:
            data.append([df["service_id"][ind], date_time_obj, day])
        # print(data)
        start_date += 1
        # print(start_date)

final_df = pd.DataFrame(data, columns=["service_id", "date", "day"])
print(final_df.count())
final_df.reset_index(drop=True)

final_df.to_sql("calendar3sept", engine)
print("done")


# Run below code in sql to remove and add the exception

# delete
# from
# 	calendar3sept c
# where
# 	exists (
# 	select
# 		*
# 	from
# 		"gtfs3Sept_calendar_dates" g
# 	where
# 		g.service_id = c.service_id
# 		and to_date(g."date"::text, 'YYYYMMDD')= c."date"
# 			and g.exception_type = 2
# );

# alter table calendar3sept add column exception varchar(10);

# insert into calendar3sept
# select null,service_id,
#     to_date("date"::text, 'YYYYMMDD'),
#     to_char(to_date("date"::text, 'YYYYMMDD')::date, 'Day'),
#     '1'
# from "gtfs3Sept_calendar_dates"
# where exception_type = '1';
