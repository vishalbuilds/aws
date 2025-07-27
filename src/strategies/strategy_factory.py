from src.strategies.utils.s3_utils import S3Utils
from src.strategies.utils.dynamodb_utils import DynamoDBUtils
from src.strategies.workflow.s3_remove_pii import S3RemovePii

FACTORY_STRATEGIES = {
    's3_remove_pii': S3RemovePii,
    's3_utils': S3Utils,
    'dynamodb_utils': DynamoDBUtils,
}

class StrategyFactory:
    def handle_request(self, request_type, event):
        strategy_class = FACTORY_STRATEGIES.get(request_type)
        if not strategy_class:
            # log "Strategy not exist"
            return {"error": "Strategy does not exist"}
        strategy = strategy_class()
        if not strategy.validate_input(event):
            # log "Invalid event"
            return {"error": "Invalid input"}
        return strategy.execute(event)
