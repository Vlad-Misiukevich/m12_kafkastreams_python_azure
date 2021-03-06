from dateutil.parser import parse as parse_date
import faust
import logging


class ExpediaRecord(faust.Record):
    id: float
    date_time: str
    site_name: int
    posa_container: int
    user_location_country: int
    user_location_region: int
    user_location_city: int
    orig_destination_distance: float
    user_id: int
    is_mobile: int
    is_package: int
    channel: int
    srch_ci: str
    srch_co: str
    srch_adults_cnt: int
    srch_children_cnt: int
    srch_rm_cnt: int
    srch_destination_id: int
    srch_destination_type_id: int
    hotel_id: int


class ExpediaExtRecord(ExpediaRecord):
    stay_category: str


logger = logging.getLogger(__name__)
app = faust.App('kafkastreams', broker='kafka://kafka:9092')
source_topic = app.topic('expedia', value_type=ExpediaRecord)
destination_topic = app.topic('expedia_ext', value_type=ExpediaExtRecord)


@app.agent(source_topic, sink=[destination_topic])
async def handle(messages):
    async for message in messages:
        if message is None:
            logger.info('No messages')
            continue
        data = message.dumps()
        if (parse_date(message.srch_co) - parse_date(message.srch_ci)).days > 14:
            stay_category = "Long stay"
        elif 10 < (parse_date(message.srch_co) - parse_date(message.srch_ci)).days <= 14:
            stay_category = "Standard extended stay"
        elif 4 < (parse_date(message.srch_co) - parse_date(message.srch_ci)).days <= 10:
            stay_category = "Standard stay"
        elif 0 < (parse_date(message.srch_co) - parse_date(message.srch_ci)).days <= 4:
            stay_category = "Short stay"
        else:
            stay_category = "Erroneous data"
        yield ExpediaExtRecord(**data, stay_category=stay_category)


if __name__ == '__main__':
    app.main()
