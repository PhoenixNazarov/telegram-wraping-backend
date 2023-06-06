# from modules.accounts.account_category_repository_json import AccountCategoryRepositoryJson
from modules.accounts.account_control_service import AccountControlService
from modules.accounts.accounts_repository_impl import AccountsRepositoryImpl
from modules.messages.massage_service import MessageService
from modules.names.names_repository_json import NamesRepositoryJson
from modules.names.names_service import NamesService
from modules.names.parsing_repository_json import ParsingRepositoryJson
from modules.names.parsing_service import ParsingService
from modules.proxy.proxy_repository import ProxyRepository
from modules.proxy.proxy_repository_impl import ProxyRepositoryJson
from modules.proxy.proxy_service import ProxyService
from modules.subscriptions.subscriptions_repository_json import SubscriptionRepositoryJson
from modules.subscriptions.subscriptions_service import SubscriptionsService
from modules.utils.config import Config


def create_names_service() -> NamesService:
    return NamesService(
        NamesRepositoryJson(Config.NamesRepositoryJson_path)
    )


def create_account_control_service() -> AccountControlService:
    return AccountControlService(
        AccountsRepositoryImpl(Config.AccountsRepositoryImpl_path),
        AccountCategoryRepositoryJson(Config.AccountCategoryRepositoryJson_path),
        create_names_service(),
        create_proxy_service()
    )


def create_parsing_service() -> ParsingService:
    return ParsingService(
        ParsingRepositoryJson(Config.ParsingRepositoryJson_path),
        create_names_service(),
        create_account_control_service(),
        create_proxy_service()
    )


def create_subscriptions_service() -> SubscriptionsService:
    return SubscriptionsService(
        create_account_control_service(),
        SubscriptionRepositoryJson(Config.SubscriptionRepositoryJson_path)
    )


def create_proxy_repository() -> ProxyRepository:
    return ProxyRepositoryJson(Config.ProxyRepositoryJson_path)


def create_proxy_service() -> ProxyService:
    return ProxyService(
        create_proxy_repository()
    )


def create_messages_service() -> MessageService:
    return MessageService(
        create_account_control_service(),
        create_proxy_service()
    )
