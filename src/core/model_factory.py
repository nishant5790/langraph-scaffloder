"""Factory for creating language models from different providers."""

from typing import Any, Dict, Optional
from langchain_core.language_models import BaseLLM
from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock

from ..config import get_settings
from ..models import ModelConfig, ModelProvider


class ModelFactory:
    """Factory class for creating language models."""
    
    @staticmethod
    def create_model(config: ModelConfig, **kwargs) -> BaseLLM:
        """Create a language model based on the configuration.
        
        Args:
            config: Model configuration
            **kwargs: Additional model parameters
            
        Returns:
            Configured language model
            
        Raises:
            ValueError: If the provider is not supported
        """
        settings = get_settings()
        
        if config.provider == ModelProvider.OPENAI:
            return ModelFactory._create_openai_model(config, settings, **kwargs)
        elif config.provider == ModelProvider.BEDROCK:
            return ModelFactory._create_bedrock_model(config, settings, **kwargs)
        else:
            raise ValueError(f"Unsupported model provider: {config.provider}")
    
    @staticmethod
    def _create_openai_model(
        config: ModelConfig, 
        settings: Any, 
        **kwargs
    ) -> ChatOpenAI:
        """Create an OpenAI model."""
        model_kwargs = {
            "model": config.model_name,
            "temperature": config.temperature,
            "api_key": settings.openai_api_key,
            **kwargs
        }
        
        if config.max_tokens:
            model_kwargs["max_tokens"] = config.max_tokens
        if config.top_p:
            model_kwargs["top_p"] = config.top_p
            
        return ChatOpenAI(**model_kwargs)
    
    @staticmethod
    def _create_bedrock_model(
        config: ModelConfig, 
        settings: Any, 
        **kwargs
    ) -> ChatBedrock:
        """Create a Bedrock model."""
        model_kwargs = {
            "model_id": config.model_name,
            "region_name": settings.aws_default_region,
            "model_kwargs": {
                "temperature": config.temperature,
            },
            **kwargs
        }
        
        if config.max_tokens:
            model_kwargs["model_kwargs"]["max_tokens"] = config.max_tokens
        if config.top_p:
            model_kwargs["model_kwargs"]["top_p"] = config.top_p
            
        # Set AWS credentials if provided
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            model_kwargs.update({
                "credentials_profile_name": None,
                "aws_access_key_id": settings.aws_access_key_id,
                "aws_secret_access_key": settings.aws_secret_access_key,
            })
            
        return ChatBedrock(**model_kwargs)
    
    @staticmethod
    def get_supported_models() -> Dict[ModelProvider, list]:
        """Get a list of supported models for each provider.
        
        Returns:
            Dictionary mapping providers to their supported models
        """
        return {
            ModelProvider.OPENAI: [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-4-turbo-preview",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
            ],
            ModelProvider.BEDROCK: [
                "anthropic.claude-3-opus-20240229-v1:0",
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "anthropic.claude-3-haiku-20240307-v1:0",
                "anthropic.claude-v2:1",
                "anthropic.claude-v2",
                "anthropic.claude-instant-v1",
                "amazon.titan-text-express-v1",
                "amazon.titan-text-lite-v1",
                "ai21.j2-ultra-v1",
                "ai21.j2-mid-v1",
                "cohere.command-text-v14",
                "meta.llama2-70b-chat-v1",
                "meta.llama2-13b-chat-v1",
            ]
        }
    
    @staticmethod
    def validate_model_config(config: ModelConfig) -> bool:
        """Validate if the model configuration is supported.
        
        Args:
            config: Model configuration to validate
            
        Returns:
            True if the configuration is valid
            
        Raises:
            ValueError: If the configuration is invalid
        """
        supported_models = ModelFactory.get_supported_models()
        
        if config.provider not in supported_models:
            raise ValueError(f"Unsupported provider: {config.provider}")
        
        if config.model_name not in supported_models[config.provider]:
            raise ValueError(
                f"Unsupported model '{config.model_name}' for provider '{config.provider}'. "
                f"Supported models: {supported_models[config.provider]}"
            )
        
        return True 