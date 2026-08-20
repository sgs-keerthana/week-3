import os.path
import datetime
from langchain_core.tools import tool
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

#Calendar Permission
SCOPES=[ "https://www.googleapis.com/auth/calendar"]
def get_calendar_service():
    creds=None
    #check whether we already have authorization
    if os.path.exists("token.json"):
        creds=Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )
    #if not authorized, ask the user to login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow=InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds=flow.run_local_server(port=0)
        #save authorization for next time
        with open("token.json","w")as token:
            token.write(creds.to_json())
    #Create calendar API service
    service=build(
        "calendar",
        "v3",
         credentials=creds
    )
    return service
@tool
def calendar_tool(action: str,
                  title: str="",
                  date: str ="",
                  time: str="",
                  duration_minutes:int=60)->str:
    """
    Manage the user's Google Calendar.
    Actions:
    -get_events:get upcoming calendar events.
    -find_free_slot:find a free time slot.
    -create_event:create a new calendar event.
    """
    service=get_calendar_service()

    #1.GET EVENTS
    if action=="get_events":
        now=datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat()
        events_result=(
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime"
            )
            .execute()
        )
        events=events_result.get(
            "items",
             []                  
        )
        if not events:
            return "No upcoming events found."
        result=[]
        for event in events:
            start=event["start"].get(
                "dateTime",
                event["start"].get("date")
            )
            event_title=event.get(
                "summary",
                "No title"
            )
            result.append(
                f"{start}-{event_title}"
            )
        return "\n".join(result)

        # FIND FREE SLOT
    elif action =="find_free_slot":
        if not date:
            return "Please provide a date."
        try:
            selected_date=datetime.date.fromisoformat(date)
        except ValueError:
            return "Date must be in YYYY-MM-DD format."
        #Search from 9AM to 6PM
        start_time=datetime.datetime.combine(
            selected_date,
            datetime.time(9,0)
        ).astimezone()

        end_time=datetime.datetime.combine(
            selected_date,
            datetime.time(18,0)
        ).astimezone()

        events_result=(
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy="startTime"
            ).execute()
        )
        events=events_result.get(
            "items",
            []
        )

        #Check 1-hour slots
        current_time=start_time
        while current_time+datetime.timedelta(
            minutes=duration_minutes
        )<= end_time:
            slot_end=current_time+datetime.timedelta(
                minutes=duration_minutes
            )
            conflict=False
            for event in events:
                event_start=event["start"].get(
                    "dateTime"
                )
                event_end=event["end"].get(
                    "dateTime"
                )
                if not event_start or not event_end:
                    continue
                event_start=datetime.datetime.fromisoformat(
                    event_start
                )
                event_end=datetime.datetime.fromisoformat(
                    event_end
                )
                if(
                    current_time<event_end
                    and slot_end>event_start
                ):
                    conflict=True
                    break
            if not conflict:
                return(
                    f"Free slot found on{date}:"
                    f"{current_time.strftime('%I:%M %p')}-"
                    f"{slot_end.strftime('%I:%M %p')}"
                )
            current_time +=datetime.timedelta(
                minutes=30
            )
        return f"No free slot found on{date}."
    # CREATE EVENT
    elif action =="create_event":
        if not title:
            return "Please provide an event title."
        if not date or not time:
            return "Please provide the date and time."
        try:
            start_datetime=datetime.datetime.fromisoformat(
                f"{date}T{time}"
            )
        except ValueError:
            return "Date must be YYYY-MM-DD and time must be HH:MM."
        end_datetime=start_datetime+datetime.timedelta(
            minutes=duration_minutes
        )
        event={
            "summary":title,
            "start":{
                "dateTime":start_datetime.isoformat(),
                "timeZone":"Asia/Kolkata"
            },
            "end":{
                "dateTime":end_datetime.isoformat(),
                "timeZone":"Asia/Kolkata"
            }
        }
        created_event=(
            service.events()
            .insert(
                calendarId="primary",
                body=event
            )
            .execute()
        )
        return(
            f"Event created successfully:{title}"
            f"on{date} at {time}."
        )
    # INVALID ACTION
    else:
        return(
            "Invalid calendar action."
            "Use get_events,find_free_slot,or create_event."
        )
