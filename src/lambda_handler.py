from src.strategies.strategy_factory import StrategyFactory
from src.common.response_builder import ResponseBuilder


def lambda_handler(event, context):
    # Remove secure info, possibly sanitize event here
    clean_event = remove_secure_info(event)  # define this function separately if needed

    request_type = clean_event.get('request_type')
    factory = StrategyFactory()
    response = factory(request_type, clean_event)

    return HandlerResponse(result="success", data=response)
