import os
import base64
from langchain_core.tools import tool
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES=["https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/gmail.modify"
]
def get_gmail_service():
    creds=None
    if os.path.exists("token_gmail.json"):
        creds=Credentials.from_authorized_user_file(
            "token_gmail.json",
             SCOPES
        )
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow=InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                 SCOPES
            )
            creds=flow.run_local_server(port=0)
        with open("token_gmail.json","w")as token:
            token.write(
                creds.to_json()
            )
    service=build(
        "gmail",
         "v1",
         credentials=creds
    )
    return service
def extract_email_body(payload):
    """
    Recursively extract the text/plain body
    from a gmail message payload
    """
    #check direct body
    body_data=payload.get("body",{}).get("data")
    if body_data:
        return base64.urlsafe_b64decode(
            body_data
        ).decode(
            "utf-8",
            errors="ignore"
        )
    #check nested parts
    for part in payload.get("parts",[]):
        if part.get("mimeType")=="text/plain":
            data=part.get(
                "body",
                {}
            ).get("data")
            if data:
                return base64.urlsafe_b64decode(
                    data
                ).decode(
                    "utf-8",
                    errors="ignore"
                )
            #Recursively check nested parts
            if part.get("parts"):
                body=extract_email_body(part)
                if body:
                    return body
        return""
#GMAIL TOOL
@tool
def gmail_tool(
    action: str,
    query: str="",
    message_id: str="",
    to: str="",
    subject: str="",
    body: str="",
    label: str=""
)->str:
    """
    Manage the user's Gmail.

Actions:

- search_email: Search emails using Gmail search queries.
  Examples:
  - Recent emails: newer_than:7d
  - Emails from today: newer_than:1d
  - Emails from this month: newer_than:30d
  - Search by subject: subject:"Security alert"
  - Search by sender: from:example@gmail.com

- read_email: Read a specific email using its message ID.

- create_draft: Create an email draft.
- label_email: apply a gmail label to an email.
  Allowed lables:
  Spam,Leave,Work,Finance,Meeting,Other.
    """
    service=get_gmail_service()

    #1.SEARCH EMAIL
    if action=="search_email":
        if not query:
            return "Please provide an email search query."
        results=(
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                maxResults=10
            )
            .execute()
        )

        messages=results.get(
            "messages",
            []
        )
        if not messages:
            return "No matching emails found."
        result=[]
        for message in messages:
            message_data=(
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=message["id"],
                    format="metadata",
                    metadataHeaders=[
                        "From",
                        "To",
                        "Subject",
                        "Date"
                    ]
                )
                .execute()
            )
            headers=message_data.get(
                "payload",
                {}
            ).get(
                "headers",
                []
            )
            header_data={}
            for header in headers:
                header_data[
                    header["name"]
                ] = header["value"]
            result.append(
                f"ID:{message['id']}\n"
                f"From:{header_data.get('From','')}\n"
                f"Subject: {header_data.get('Subject','')}\n"
                f"Date:{header_data.get('Date','')}"
            )
            return"\n\n".join(result)
    #2. READ EMAIL
    elif action =="read_email":
        if not message_id:
            return "Please provide an email message ID."
        message=(
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full"
            )
            .execute()
        )
        payload=message.get(
            "payload",
            {}
        )
        #Extractn email body
        email_body=extract_email_body(
            payload
        )
        #Extract headers
        headers=payload.get(
            "headers",
            []
        )
        header_data={}
        for header in headers:
            header_data[
                header["name"]
            ] = header["value"]
        return(
            f"MessageID:{message_id}\n"
            f"From:{header_data.get('From','')}\n"
            f"To:{header_data.get('To','')}\n"
            f"Subject:{header_data.get('Subject','')}\n"
            f"Date: {header_data.get('Date','')}\n\n"
            f"Email Body:\n{email_body}"
        )

        
        
    #3. CREATE DRAFT
    elif action =="create_draft":
        if not to:
            return "Please provide the recipient."
        if not subject:
            return "Please provide the subject."
        if not body:
            return "Please provide the email body."
        email_message=(
            f"To: {to}\r\n"
            f"Subject: {subject}\r\n"
            f"\r\n"
            f"{body}"
        )
        encoded_message=base64.urlsafe_b64encode(
            email_message.encode("utf-8")
        ).decode("utf-8")

        draft_body={
            "message":{
                "raw":encoded_message
            }
        }
        draft=(
            service.users()
            .drafts()
            .create(
                userId="me",
                body=draft_body
            )
            .execute()
        )
        return(
            f"Draft created Successfully. "
            f"Draft ID: {draft['id']}"
        )
    #4.Apply gmail label
    elif action=="label_email":
        if not message_id:
            return "Please provide the email message ID."
        if not label:
            return "Please provide the label."
        allowed_labels=[
            "Spam",
            "Leave",
            "Work",
            "Finance",
            "Meeting",
            "Other"
        ]
        if label not in allowed_labels:
            return(
                "Invalid label. "
                "Use Spam,Leave,Work,Finance,Meeting,or Other."
            )
        #Get existing gmail labels
        labels_result=(
            service.users()
            .labels()
            .list(
                userId="me"
            )
            .execute()
        )
        labels=labels_result.get(
            "labels",
            []
        )
        label_id=None
        #Check whether label already exists
        for gmail_label in labels:
            if gmail_label.get("name")==label:
                label_id=gmail_label.get("id")
                break
        #create label if it doesn't exist
        if label_id is None:
            created_label=(
                service.users()
                .labels()
                .create(
                    userId="me",
                    body={
                        "name":label
                    }
                )
                .execute()
            )
            label_id=created_label["id"]
        #Apply label to the email
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={
                "addLabelIds":[label_id]
            }
        ).execute()
        return(
            f"Email labeled succesfully as '{label}'."
        )
    
    else:
        return(
            "Invalid Gmail action. "
            "Use search_email,read_email,or create_draft, "
            "or label_email."
        ) 

    