"""
This module defines Pydantic models for various Bitwarden entities.

Classes:
    BwItemLoginFido2Credentials: Represents Fido2 credentials associated with a Bitwarden login item.
    SSHKey: Represents an SSH key.
    BwItemLoginUri: Represents a URI associated with a Bitwarden login item.
    BwItemLogin: Represents a Bitwarden login item.
    BWCard: Represents a credit card associated with a Bitwarden item.
    BwIdentity: Represents an identity associated with a Bitwarden item.
    BwItemPasswordHistory: Represents the password history of a Bitwarden item.
    BwItemAttachment: Represents an attachment associated with a Bitwarden item.
    BwField: Represents a custom field associated with a Bitwarden item.
    BwItem: Represents a Bitwarden item.
    BwCollection: Represents a collection of Bitwarden items.
    BwOrganization: Represents a Bitwarden organization.
    BwFolder: Represents a folder in Bitwarden.

"""

from typing import Dict, List, Optional

from pydantic import BaseModel


class BwItemLoginFido2Credentials(BaseModel):
    """
    Bitwarden Fido2 Credentials Model.
    """

    credentialId: str
    keyType: str
    keyAlgorithm: str
    keyCurve: str
    keyValue: str
    rpId: str
    userHandle: str
    userName: Optional[str] = None
    counter: str
    rpName: str
    userDisplayName: str
    discoverable: str
    creationDate: str


class BwItemLoginUri(BaseModel):
    """
    Bitwarden Login URI Model.
    """

    match: Optional[int] = None
    uri: str


class BwIdentity(BaseModel):
    """
    Bitwarden Identity Model.
    """

    title: Optional[str] = None
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    lastName: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    address3: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    ssn: Optional[str] = None
    username: Optional[str] = None
    passportNumber: Optional[str] = None
    licenseNumber: Optional[str] = None


class BwCard(BaseModel):
    """
    Bitwarden Card Model.
    """

    cardholderName: Optional[str] = None
    brand: str
    number: Optional[str] = None
    expMonth: Optional[str] = None
    expYear: Optional[str] = None
    code: Optional[str] = None


class BwItemLogin(BaseModel):
    """
    Bitwarden Login Model.
    """

    username: Optional[str] = None
    password: Optional[str] = None
    totp: Optional[str] = None
    uris: List[BwItemLoginUri] = []
    passwordRevisionDate: Optional[str] = None
    fido2Credentials: Optional[List[BwItemLoginFido2Credentials]] = None


class BwItemPasswordHistory(BaseModel):
    """
    Bitwarden Password History Model.
    """

    lastUsedDate: str
    password: str


class BwItemAttachment(BaseModel):
    """
    Bitwarden Attachment Model.
    """

    id: str
    fileName: str
    size: str
    sizeName: str
    url: str
    local_file_path: str = ""


class SSHKey(BaseModel):
    """
    SSH Key Model.
    """

    privateKey: str
    publicKey: str
    keyFingerprint: str


class BwField(BaseModel):
    """
    Bitwarden Field Model
    """

    name: str
    value: Optional[str] = None
    type: int
    linkedId: Optional[int] = None


class BwItem(BaseModel):
    """
    Bitwarden Item Model.

    Attributes:
        passwordHistory: Optional previous passwords for the item.
        revisionDate: ISO date-time when the item was last modified.
        creationDate: ISO date-time when the item was created.
        deletedDate: ISO date-time when the item was deleted, if applicable.
        object: Bitwarden object type string (e.g., "item").
        id: Unique identifier of the item.
        organizationId: Organization ID if the item belongs to an organization.
        folderId: Folder ID if the item belongs to a personal folder.
        type: Numeric BW item type (1=login, 2=secure note, 3=card, 4=identity, etc.).
        reprompt: Reprompt policy value.
        name: Human-readable item title.
        notes: Optional freeform notes.
        favorite: Whether the item is marked as favorite.
        login: Login-specific details (username/password/uris/totp), if any.
        sshKey: Optional SSH key bundle if stored with the item.
        collectionIds: Organization collection IDs this item belongs to.
        attachments: Attachments metadata.
        fields: Custom fields defined on the item.
        card: Credit card details if type is card.
        identity: Identity details if type is identity.
    """

    passwordHistory: Optional[List[BwItemPasswordHistory]] = None
    revisionDate: str
    creationDate: str
    deletedDate: Optional[str] = None
    object: str
    id: str
    organizationId: Optional[str] = None
    folderId: Optional[str] = None
    type: int
    reprompt: int
    name: str
    notes: Optional[str] = None
    favorite: bool
    login: Optional[BwItemLogin] = None
    sshKey: Optional[SSHKey] = None
    collectionIds: List[str] = []
    attachments: List[BwItemAttachment] = []
    fields: List[BwField] = []
    card: Optional[BwCard] = None
    identity: Optional[BwIdentity] = None


class BwCollection(BaseModel):
    """
    Bitwarden Collection Model.

    Attributes:
        object: Bitwarden object type (e.g., "collection").
        id: Unique identifier of the collection.
        organizationId: ID of the parent organization.
        name: Collection name.
        externalId: Optional external reference.
        items: Mutable mapping of item ID to BwItem, used during export organization.
    """

    object: str
    id: str
    organizationId: str
    name: str
    externalId: Optional[str] = None
    items: Dict[str, BwItem] = {}


class BwOrganization(BaseModel):
    """
    Bitwarden Organization Model.

    Attributes:
        object: Bitwarden object type (e.g., "organization").
        id: Unique identifier of the organization.
        name: Organization name.
        status: Organization status code.
        type: Organization type code.
        enabled: Whether the organization is enabled.
        collections: Collections keyed by collection ID.
    """

    object: str
    id: str
    name: str
    status: int
    type: int
    enabled: bool
    collections: Dict[str, BwCollection] = {}


class BwFolder(BaseModel):
    """
    Bitwarden Folder Model.

    Attributes:
        object: Bitwarden object type (e.g., "folder").
        id: Optional folder ID; may be None for the implicit "No Folder".
        name: Folder name.
        items: Items keyed by item ID within this folder bucket.
    """

    object: str
    id: Optional[str] = None
    name: str
    items: Dict[str, BwItem] = {}
