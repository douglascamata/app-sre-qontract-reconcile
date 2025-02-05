"""
Generated by qenerate plugin=pydantic_v1. DO NOT MODIFY MANUALLY!
"""
from collections.abc import Callable  # noqa: F401 # pylint: disable=W0611
from enum import Enum  # noqa: F401 # pylint: disable=W0611
from typing import (  # noqa: F401 # pylint: disable=W0611
    Any,
    Optional,
    Union,
)

from pydantic import (  # noqa: F401 # pylint: disable=W0611
    BaseModel,
    Extra,
    Field,
    Json,
)

from reconcile.gql_definitions.fragments.user import User


DEFINITION = """
fragment User on User_v1 {
  name
  org_username
  github_username
  slack_username
  pagerduty_username
}

query SlackUsergroupClusterUser {
  users: users_v1 {
    ...User
    tag_on_cluster_updates
    roles {
      tag_on_cluster_updates
      access {
        cluster {
          name
        }
        namespace {
          name
          cluster {
            name
          }
        }
      }
    }
  }
}
"""


class ClusterV1(BaseModel):
    name: str = Field(..., alias="name")

    class Config:
        smart_union = True
        extra = Extra.forbid


class NamespaceV1_ClusterV1(BaseModel):
    name: str = Field(..., alias="name")

    class Config:
        smart_union = True
        extra = Extra.forbid


class NamespaceV1(BaseModel):
    name: str = Field(..., alias="name")
    cluster: NamespaceV1_ClusterV1 = Field(..., alias="cluster")

    class Config:
        smart_union = True
        extra = Extra.forbid


class AccessV1(BaseModel):
    cluster: Optional[ClusterV1] = Field(..., alias="cluster")
    namespace: Optional[NamespaceV1] = Field(..., alias="namespace")

    class Config:
        smart_union = True
        extra = Extra.forbid


class RoleV1(BaseModel):
    tag_on_cluster_updates: Optional[bool] = Field(..., alias="tag_on_cluster_updates")
    access: Optional[list[AccessV1]] = Field(..., alias="access")

    class Config:
        smart_union = True
        extra = Extra.forbid


class UserV1(User):
    tag_on_cluster_updates: Optional[bool] = Field(..., alias="tag_on_cluster_updates")
    roles: Optional[list[RoleV1]] = Field(..., alias="roles")

    class Config:
        smart_union = True
        extra = Extra.forbid


class SlackUsergroupClusterUserQueryData(BaseModel):
    users: Optional[list[UserV1]] = Field(..., alias="users")

    class Config:
        smart_union = True
        extra = Extra.forbid


def query(query_func: Callable, **kwargs: Any) -> SlackUsergroupClusterUserQueryData:
    """
    This is a convenience function which queries and parses the data into
    concrete types. It should be compatible with most GQL clients.
    You do not have to use it to consume the generated data classes.
    Alternatively, you can also mime and alternate the behavior
    of this function in the caller.

    Parameters:
        query_func (Callable): Function which queries your GQL Server
        kwargs: optional arguments that will be passed to the query function

    Returns:
        SlackUsergroupClusterUserQueryData: queried data parsed into generated classes
    """
    raw_data: dict[Any, Any] = query_func(DEFINITION, **kwargs)
    return SlackUsergroupClusterUserQueryData(**raw_data)
