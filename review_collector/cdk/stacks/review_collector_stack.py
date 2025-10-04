"""
CDK Stack for Review Collector System with SerpAPI

This stack creates:
- Lambda Function for SerpAPI-based review collection
- Lambda Layer for shared code
- API Gateway for HTTP access
- DynamoDB table for storing reviews
- Secrets Manager for API keys
"""

from pathlib import Path
from typing import Dict, Any

from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
)
from constructs import Construct


class ReviewCollectorStack(Stack):
    """
    CDK Stack for SerpAPI-based Review Collector.
    
    Architecture:
    - Single Lambda function for all review sources (App Store, Google Play, Trustpilot)
    - Lambda Layer for shared domain/application/infrastructure code
    - API Gateway for on-demand collection
    - DynamoDB for review storage
    - Secrets Manager for SerpAPI key
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Base path for Lambda code
        base_path = Path(__file__).parent.parent.parent / "src"
        
        # 1. Create DynamoDB Tables
        reviews_table = self._create_dynamodb_table()
        processed_data_table = self._create_processed_data_table()
        
        # 2. Create Secrets Manager Secret
        secret = self._create_secrets_manager()
        
        # 3. Create Lambda Layer for shared code
        shared_layer = self._create_shared_layer(base_path)
        
        # 4. Create Lambda Function for SerpAPI collection
        serpapi_lambda = self._create_serpapi_lambda(
            base_path=base_path,
            table=reviews_table,
            secret=secret,
            shared_layer=shared_layer
        )
        
        # 5. Create Lambda Function for News collection
        news_lambda = self._create_news_lambda(
            base_path=base_path,
            table=reviews_table,
            secret=secret,
            shared_layer=shared_layer
        )
        
        # 6. Create API Gateway
        api = self._create_api_gateway(serpapi_lambda, news_lambda, reviews_table)
    
    def _create_dynamodb_table(self) -> dynamodb.Table:
        """Create DynamoDB table for storing reviews with pk as primary key."""
        table = dynamodb.Table(
            self,
            "ReviewsTableV2",
            table_name="ReviewsTableV2",
            partition_key=dynamodb.Attribute(
                name="pk",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
        )
        
        # GSI for querying by brand
        table.add_global_secondary_index(
            index_name="brand-created_at-index",
            partition_key=dynamodb.Attribute(
                name="brand",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
        )
        
        return table
    
    def _create_processed_data_table(self) -> dynamodb.Table:
        """
        Create DynamoDB table for storing processed review data.
        
        Schema:
        - id (pk): Unique identifier for the processed review
        - source: Source platform (e.g., "app_store", "google_play", "trustpilot")
        - backlink: URL to original review
        - text: Review text content
        - rating: Numeric rating (0-5)
        - created_at: ISO timestamp when review was created
        - sentiment: Sentiment analysis result (e.g., "positive", "negative", "neutral")
        - description: Additional description or summary
        - category: Review category classification
        - isProcessed: Boolean flag indicating processing status
        """
        table = dynamodb.Table(
            self,
            "ProcessedDataTable",
            table_name="ProcessedDataTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
        )
        
        # GSI for querying by source and created_at
        table.add_global_secondary_index(
            index_name="source-created_at-index",
            partition_key=dynamodb.Attribute(
                name="source",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
        )
        
        # GSI for querying by sentiment and created_at
        table.add_global_secondary_index(
            index_name="sentiment-created_at-index",
            partition_key=dynamodb.Attribute(
                name="sentiment",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
        )
        
        # GSI for querying by category and rating
        table.add_global_secondary_index(
            index_name="category-rating-index",
            partition_key=dynamodb.Attribute(
                name="category",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="rating",
                type=dynamodb.AttributeType.NUMBER
            ),
        )
        
        # GSI for querying unprocessed items
        table.add_global_secondary_index(
            index_name="isProcessed-created_at-index",
            partition_key=dynamodb.Attribute(
                name="isProcessed",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
        )
        
        return table
    
    def _create_secrets_manager(self) -> secretsmanager.Secret:
        """Create or reference Secrets Manager secret."""
        # Reference existing secret (created manually with SerpAPI key)
        secret = secretsmanager.Secret.from_secret_name_v2(
            self,
            "ReviewCollectorSecret",
            secret_name="review-collector/credentials"
        )
        
        return secret
    
    def _create_shared_layer(self, base_path: Path) -> lambda_.LayerVersion:
        """Create Lambda Layer for shared code (domain, application, infrastructure)."""
        shared_path = str(base_path / "shared")
        
        layer = lambda_.LayerVersion(
            self,
            "SharedCodeLayer",
            layer_version_name="review-collector-shared",
            code=lambda_.Code.from_asset(
                shared_path,
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_11.bundling_image,
                    "command": [
                        "bash", "-c",
                        "mkdir -p /asset-output/python && "
                        "cp -r . /asset-output/python/"
                    ],
                }
            ),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
            description="Shared domain, application, and infrastructure code"
        )
        
        return layer
    
    def _create_serpapi_lambda(
        self,
        base_path: Path,
        table: dynamodb.Table,
        secret: secretsmanager.Secret,
        shared_layer: lambda_.LayerVersion
    ) -> lambda_.Function:
        """Create unified Lambda function for SerpAPI-based collection."""
        src_path = str(base_path / "serpapi_collector")
        
        fn = lambda_.Function(
            self,
            "SerpAPICollectorLambda",
            function_name="serpapi-collector-lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(
                src_path,
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_11.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && "
                        "cp -r . /asset-output/"
                    ],
                }
            ),
            layers=[shared_layer],
            timeout=Duration.seconds(120),  # Extended for DataForSEO polling (can take 30-90 sec)
            memory_size=512,
            environment={
                "TABLE_NAME": table.table_name,
                "SECRET_NAME": secret.secret_name,
                "POWERTOOLS_SERVICE_NAME": "review-collector",
                "LOG_LEVEL": "INFO",
            },
        )
        
        # Grant permissions
        table.grant_read_write_data(fn)
        secret.grant_read(fn)
        
        return fn
    
    def _create_news_lambda(
        self,
        base_path: Path,
        table: dynamodb.Table,
        secret: secretsmanager.Secret,
        shared_layer: lambda_.LayerVersion
    ) -> lambda_.Function:
        """Create Lambda function for NewsAPI-based collection."""
        src_path = str(base_path / "news_collector")
        
        fn = lambda_.Function(
            self,
            "NewsCollectorLambda",
            function_name="news-collector-lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(
                src_path,
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_11.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && "
                        "cp -r . /asset-output/"
                    ],
                }
            ),
            layers=[shared_layer],
            timeout=Duration.seconds(120),
            memory_size=512,
            environment={
                "TABLE_NAME": table.table_name,
                "SECRET_NAME": secret.secret_name,
                "POWERTOOLS_SERVICE_NAME": "news-collector",
                "LOG_LEVEL": "INFO",
            },
        )
        
        # Grant permissions
        table.grant_read_write_data(fn)
        secret.grant_read(fn)
        
        return fn
    
    def _create_api_gateway(
        self,
        review_lambda: lambda_.Function,
        news_lambda: lambda_.Function,
        table: dynamodb.Table
    ) -> apigateway.RestApi:
        """Create API Gateway for HTTP access."""
        api = apigateway.RestApi(
            self,
            "ReviewCollectorAPI",
            rest_api_name="Review Collector API",
            description="API for on-demand review and news collection",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
        )
        
        # Integration for review collection
        review_integration = apigateway.LambdaIntegration(
            review_lambda,
            proxy=True,
            allow_test_invoke=True,
        )
        
        # POST /collect-reviews endpoint
        collect_reviews_resource = api.root.add_resource("collect-reviews")
        collect_reviews_resource.add_method("POST", review_integration)
        
        # Add CORS for reviews
        collect_reviews_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )
        
        # Integration for news collection
        news_integration = apigateway.LambdaIntegration(
            news_lambda,
            proxy=True,
            allow_test_invoke=True,
        )
        
        # POST /collect-news endpoint
        collect_news_resource = api.root.add_resource("collect-news")
        collect_news_resource.add_method("POST", news_integration)
        
        # Add CORS for news
        collect_news_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )
        
        # Stack outputs
        from aws_cdk import CfnOutput
        
        CfnOutput(
            self,
            "ApiUrl",
            value=api.url,
            description="API Gateway URL"
        )
        
        CfnOutput(
            self,
            "CollectReviewsEndpoint",
            value=f"{api.url}collect-reviews",
            description="Collect Reviews Endpoint"
        )
        
        CfnOutput(
            self,
            "CollectNewsEndpoint",
            value=f"{api.url}collect-news",
            description="Collect News Endpoint"
        )
        
        CfnOutput(
            self,
            "ReviewLambdaFunctionName",
            value=review_lambda.function_name,
            description="Review Lambda Function Name"
        )
        
        CfnOutput(
            self,
            "NewsLambdaFunctionName",
            value=news_lambda.function_name,
            description="News Lambda Function Name"
        )
        
        CfnOutput(
            self,
            "DynamoDBTableName",
            value=table.table_name,
            description="DynamoDB Table Name"
        )
        
        return api
