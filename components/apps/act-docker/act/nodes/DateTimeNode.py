#!/usr/bin/env python3
"""
Date/Time Node for ACT Workflow System

This node provides comprehensive date and time operations including:
- Date/time parsing and formatting
- Timezone conversions and management
- Date arithmetic (add/subtract days, months, years)
- Duration calculations and comparisons
- Business day calculations
- Calendar operations (weekdays, holidays)
- Timestamp conversions (Unix, ISO, custom formats)
- Date validation and analysis
- Recurring date patterns
- Age and time difference calculations
"""

import time
from datetime import datetime, date, timedelta, timezone
from dateutil import parser, tz, relativedelta, rrule
from dateutil.relativedelta import relativedelta as rd
import calendar
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple
import logging

from base_node import BaseNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DateTimeOperationsError(Exception):
    """Custom exception for date/time operations errors."""
    pass

class DateTimeOperation(str, Enum):
    """Enumeration of all date/time operations."""
    
    # Parsing and Formatting
    PARSE = "parse"
    FORMAT = "format"
    NOW = "now"
    TODAY = "today"
    TOMORROW = "tomorrow"
    YESTERDAY = "yesterday"
    
    # Basic Operations
    ADD_DAYS = "add_days"
    ADD_WEEKS = "add_weeks"
    ADD_MONTHS = "add_months"
    ADD_YEARS = "add_years"
    ADD_HOURS = "add_hours"
    ADD_MINUTES = "add_minutes"
    ADD_SECONDS = "add_seconds"
    
    # Subtraction Operations
    SUBTRACT_DAYS = "subtract_days"
    SUBTRACT_WEEKS = "subtract_weeks"
    SUBTRACT_MONTHS = "subtract_months"
    SUBTRACT_YEARS = "subtract_years"
    SUBTRACT_HOURS = "subtract_hours"
    SUBTRACT_MINUTES = "subtract_minutes"
    SUBTRACT_SECONDS = "subtract_seconds"
    
    # Timezone Operations
    TO_TIMEZONE = "to_timezone"
    FROM_TIMEZONE = "from_timezone"
    LIST_TIMEZONES = "list_timezones"
    GET_TIMEZONE_INFO = "get_timezone_info"
    
    # Difference Calculations
    DIFF_DAYS = "diff_days"
    DIFF_WEEKS = "diff_weeks"
    DIFF_MONTHS = "diff_months"
    DIFF_YEARS = "diff_years"
    DIFF_HOURS = "diff_hours"
    DIFF_MINUTES = "diff_minutes"
    DIFF_SECONDS = "diff_seconds"
    TIME_UNTIL = "time_until"
    TIME_SINCE = "time_since"
    AGE = "age"
    
    # Extraction Operations
    GET_YEAR = "get_year"
    GET_MONTH = "get_month"
    GET_DAY = "get_day"
    GET_HOUR = "get_hour"
    GET_MINUTE = "get_minute"
    GET_SECOND = "get_second"
    GET_WEEKDAY = "get_weekday"
    GET_QUARTER = "get_quarter"
    GET_WEEK_NUMBER = "get_week_number"
    GET_DAY_OF_YEAR = "get_day_of_year"
    
    # Comparison Operations
    IS_BEFORE = "is_before"
    IS_AFTER = "is_after"
    IS_SAME = "is_same"
    IS_BETWEEN = "is_between"
    IS_WEEKEND = "is_weekend"
    IS_WEEKDAY = "is_weekday"
    IS_LEAP_YEAR = "is_leap_year"
    
    # Calendar Operations
    START_OF_DAY = "start_of_day"
    END_OF_DAY = "end_of_day"
    START_OF_WEEK = "start_of_week"
    END_OF_WEEK = "end_of_week"
    START_OF_MONTH = "start_of_month"
    END_OF_MONTH = "end_of_month"
    START_OF_YEAR = "start_of_year"
    END_OF_YEAR = "end_of_year"
    DAYS_IN_MONTH = "days_in_month"
    
    # Business Operations
    ADD_BUSINESS_DAYS = "add_business_days"
    SUBTRACT_BUSINESS_DAYS = "subtract_business_days"
    COUNT_BUSINESS_DAYS = "count_business_days"
    IS_BUSINESS_DAY = "is_business_day"
    NEXT_BUSINESS_DAY = "next_business_day"
    PREVIOUS_BUSINESS_DAY = "previous_business_day"
    
    # Conversion Operations
    TO_TIMESTAMP = "to_timestamp"
    FROM_TIMESTAMP = "from_timestamp"
    TO_ISO = "to_iso"
    FROM_ISO = "from_iso"
    TO_UNIX = "to_unix"
    FROM_UNIX = "from_unix"
    
    # Generation Operations
    DATE_RANGE = "date_range"
    RECURRING_DATES = "recurring_dates"
    WORKING_DAYS = "working_days"
    
    # Validation Operations
    IS_VALID_DATE = "is_valid_date"
    VALIDATE_FORMAT = "validate_format"
    
    # Batch Operations
    BATCH_PARSE = "batch_parse"
    BATCH_FORMAT = "batch_format"

class DateTimeProcessor:
    """Core date/time processing engine."""
    
    def __init__(self):
        self.default_timezone = tz.UTC
        
        # Common date formats for parsing
        self.common_formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%B %d, %Y",
            "%d %B %Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z"
        ]
    
    # Parsing and Formatting
    def parse(self, date_string: str, format_string: Optional[str] = None, 
             timezone_str: Optional[str] = None) -> datetime:
        """Parse date string into datetime object."""
        try:
            if format_string:
                # Use specific format
                dt = datetime.strptime(date_string, format_string)
            else:
                # Use dateutil parser for flexible parsing
                dt = parser.parse(date_string)
            
            # Apply timezone if specified
            if timezone_str:
                target_tz = tz.gettz(timezone_str)
                if target_tz:
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=target_tz)
                    else:
                        dt = dt.astimezone(target_tz)
            
            return dt
            
        except Exception as e:
            raise DateTimeOperationsError(f"Failed to parse date '{date_string}': {str(e)}")
    
    def format(self, dt: datetime, format_string: str) -> str:
        """Format datetime object as string."""
        try:
            return dt.strftime(format_string)
        except Exception as e:
            raise DateTimeOperationsError(f"Failed to format datetime: {str(e)}")
    
    def now(self, timezone_str: Optional[str] = None) -> datetime:
        """Get current datetime."""
        if timezone_str:
            target_tz = tz.gettz(timezone_str)
            return datetime.now(target_tz)
        return datetime.now(tz.UTC)
    
    def today(self, timezone_str: Optional[str] = None) -> date:
        """Get today's date."""
        now_dt = self.now(timezone_str)
        return now_dt.date()
    
    def tomorrow(self, timezone_str: Optional[str] = None) -> date:
        """Get tomorrow's date."""
        today_dt = self.today(timezone_str)
        return today_dt + timedelta(days=1)
    
    def yesterday(self, timezone_str: Optional[str] = None) -> date:
        """Get yesterday's date."""
        today_dt = self.today(timezone_str)
        return today_dt - timedelta(days=1)
    
    # Addition Operations
    def add_days(self, dt: datetime, days: int) -> datetime:
        """Add days to datetime."""
        return dt + timedelta(days=days)
    
    def add_weeks(self, dt: datetime, weeks: int) -> datetime:
        """Add weeks to datetime."""
        return dt + timedelta(weeks=weeks)
    
    def add_months(self, dt: datetime, months: int) -> datetime:
        """Add months to datetime."""
        return dt + rd(months=months)
    
    def add_years(self, dt: datetime, years: int) -> datetime:
        """Add years to datetime."""
        return dt + rd(years=years)
    
    def add_hours(self, dt: datetime, hours: int) -> datetime:
        """Add hours to datetime."""
        return dt + timedelta(hours=hours)
    
    def add_minutes(self, dt: datetime, minutes: int) -> datetime:
        """Add minutes to datetime."""
        return dt + timedelta(minutes=minutes)
    
    def add_seconds(self, dt: datetime, seconds: int) -> datetime:
        """Add seconds to datetime."""
        return dt + timedelta(seconds=seconds)
    
    # Subtraction Operations
    def subtract_days(self, dt: datetime, days: int) -> datetime:
        """Subtract days from datetime."""
        return dt - timedelta(days=days)
    
    def subtract_weeks(self, dt: datetime, weeks: int) -> datetime:
        """Subtract weeks from datetime."""
        return dt - timedelta(weeks=weeks)
    
    def subtract_months(self, dt: datetime, months: int) -> datetime:
        """Subtract months from datetime."""
        return dt - rd(months=months)
    
    def subtract_years(self, dt: datetime, years: int) -> datetime:
        """Subtract years from datetime."""
        return dt - rd(years=years)
    
    def subtract_hours(self, dt: datetime, hours: int) -> datetime:
        """Subtract hours from datetime."""
        return dt - timedelta(hours=hours)
    
    def subtract_minutes(self, dt: datetime, minutes: int) -> datetime:
        """Subtract minutes from datetime."""
        return dt - timedelta(minutes=minutes)
    
    def subtract_seconds(self, dt: datetime, seconds: int) -> datetime:
        """Subtract seconds from datetime."""
        return dt - timedelta(seconds=seconds)
    
    # Timezone Operations
    def to_timezone(self, dt: datetime, timezone_str: str) -> datetime:
        """Convert datetime to specified timezone."""
        target_tz = tz.gettz(timezone_str)
        if not target_tz:
            raise DateTimeOperationsError(f"Invalid timezone: {timezone_str}")
        
        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            dt = dt.replace(tzinfo=tz.UTC)
        
        return dt.astimezone(target_tz)
    
    def from_timezone(self, dt: datetime, source_timezone: str, target_timezone: str = "UTC") -> datetime:
        """Convert datetime from source timezone to target timezone."""
        source_tz = tz.gettz(source_timezone)
        target_tz = tz.gettz(target_timezone)
        
        if not source_tz:
            raise DateTimeOperationsError(f"Invalid source timezone: {source_timezone}")
        if not target_tz:
            raise DateTimeOperationsError(f"Invalid target timezone: {target_timezone}")
        
        # Set source timezone if not present
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=source_tz)
        
        return dt.astimezone(target_tz)
    
    def list_timezones(self, region: Optional[str] = None) -> List[str]:
        """List available timezones."""
        import zoneinfo
        
        zones = list(zoneinfo.available_timezones())
        
        if region:
            zones = [z for z in zones if z.startswith(region)]
        
        return sorted(zones)
    
    def get_timezone_info(self, timezone_str: str, dt: Optional[datetime] = None) -> Dict[str, Any]:
        """Get timezone information."""
        target_tz = tz.gettz(timezone_str)
        if not target_tz:
            raise DateTimeOperationsError(f"Invalid timezone: {timezone_str}")
        
        if dt is None:
            dt = datetime.now(tz.UTC)
        
        dt_in_tz = dt.astimezone(target_tz)
        
        return {
            "timezone": timezone_str,
            "abbreviation": dt_in_tz.strftime("%Z"),
            "offset": dt_in_tz.strftime("%z"),
            "is_dst": bool(dt_in_tz.dst()),
            "utc_offset_seconds": int(dt_in_tz.utcoffset().total_seconds())
        }
    
    # Difference Calculations
    def diff_days(self, dt1: datetime, dt2: datetime) -> int:
        """Calculate difference in days."""
        return (dt2.date() - dt1.date()).days
    
    def diff_weeks(self, dt1: datetime, dt2: datetime) -> float:
        """Calculate difference in weeks."""
        return (dt2 - dt1).days / 7.0
    
    def diff_months(self, dt1: datetime, dt2: datetime) -> int:
        """Calculate difference in months."""
        return rd(dt2, dt1).months + (rd(dt2, dt1).years * 12)
    
    def diff_years(self, dt1: datetime, dt2: datetime) -> int:
        """Calculate difference in years."""
        return rd(dt2, dt1).years
    
    def diff_hours(self, dt1: datetime, dt2: datetime) -> float:
        """Calculate difference in hours."""
        return (dt2 - dt1).total_seconds() / 3600
    
    def diff_minutes(self, dt1: datetime, dt2: datetime) -> float:
        """Calculate difference in minutes."""
        return (dt2 - dt1).total_seconds() / 60
    
    def diff_seconds(self, dt1: datetime, dt2: datetime) -> float:
        """Calculate difference in seconds."""
        return (dt2 - dt1).total_seconds()
    
    def time_until(self, target_dt: datetime, from_dt: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate time until target datetime."""
        if from_dt is None:
            from_dt = datetime.now(tz.UTC)
        
        if target_dt.tzinfo is None:
            target_dt = target_dt.replace(tzinfo=tz.UTC)
        if from_dt.tzinfo is None:
            from_dt = from_dt.replace(tzinfo=tz.UTC)
        
        delta = target_dt - from_dt
        
        return {
            "total_seconds": delta.total_seconds(),
            "days": delta.days,
            "hours": delta.seconds // 3600,
            "minutes": (delta.seconds % 3600) // 60,
            "seconds": delta.seconds % 60,
            "is_future": delta.total_seconds() > 0
        }
    
    def time_since(self, past_dt: datetime, from_dt: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate time since past datetime."""
        if from_dt is None:
            from_dt = datetime.now(tz.UTC)
        
        return self.time_until(from_dt, past_dt)
    
    def age(self, birth_date: Union[datetime, date], reference_date: Optional[Union[datetime, date]] = None) -> Dict[str, Any]:
        """Calculate age."""
        if reference_date is None:
            reference_date = date.today()
        
        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        if isinstance(reference_date, datetime):
            reference_date = reference_date.date()
        
        delta = rd(reference_date, birth_date)
        
        return {
            "years": delta.years,
            "months": delta.months,
            "days": delta.days,
            "total_days": (reference_date - birth_date).days
        }
    
    # Extraction Operations
    def get_year(self, dt: datetime) -> int:
        """Get year from datetime."""
        return dt.year
    
    def get_month(self, dt: datetime) -> int:
        """Get month from datetime."""
        return dt.month
    
    def get_day(self, dt: datetime) -> int:
        """Get day from datetime."""
        return dt.day
    
    def get_hour(self, dt: datetime) -> int:
        """Get hour from datetime."""
        return dt.hour
    
    def get_minute(self, dt: datetime) -> int:
        """Get minute from datetime."""
        return dt.minute
    
    def get_second(self, dt: datetime) -> int:
        """Get second from datetime."""
        return dt.second
    
    def get_weekday(self, dt: datetime) -> int:
        """Get weekday (0=Monday, 6=Sunday)."""
        return dt.weekday()
    
    def get_quarter(self, dt: datetime) -> int:
        """Get quarter (1-4)."""
        return (dt.month - 1) // 3 + 1
    
    def get_week_number(self, dt: datetime) -> int:
        """Get ISO week number."""
        return dt.isocalendar()[1]
    
    def get_day_of_year(self, dt: datetime) -> int:
        """Get day of year (1-366)."""
        return dt.timetuple().tm_yday
    
    # Comparison Operations
    def is_before(self, dt1: datetime, dt2: datetime) -> bool:
        """Check if dt1 is before dt2."""
        return dt1 < dt2
    
    def is_after(self, dt1: datetime, dt2: datetime) -> bool:
        """Check if dt1 is after dt2."""
        return dt1 > dt2
    
    def is_same(self, dt1: datetime, dt2: datetime, precision: str = "second") -> bool:
        """Check if two datetimes are the same within precision."""
        if precision == "year":
            return dt1.year == dt2.year
        elif precision == "month":
            return dt1.year == dt2.year and dt1.month == dt2.month
        elif precision == "day":
            return dt1.date() == dt2.date()
        elif precision == "hour":
            return (dt1.year == dt2.year and dt1.month == dt2.month and 
                   dt1.day == dt2.day and dt1.hour == dt2.hour)
        elif precision == "minute":
            return (dt1.replace(second=0, microsecond=0) == 
                   dt2.replace(second=0, microsecond=0))
        else:  # second
            return (dt1.replace(microsecond=0) == dt2.replace(microsecond=0))
    
    def is_between(self, dt: datetime, start_dt: datetime, end_dt: datetime, 
                  inclusive: bool = True) -> bool:
        """Check if datetime is between start and end."""
        if inclusive:
            return start_dt <= dt <= end_dt
        else:
            return start_dt < dt < end_dt
    
    def is_weekend(self, dt: datetime) -> bool:
        """Check if datetime falls on weekend."""
        return dt.weekday() >= 5  # Saturday=5, Sunday=6
    
    def is_weekday(self, dt: datetime) -> bool:
        """Check if datetime falls on weekday."""
        return dt.weekday() < 5  # Monday=0 to Friday=4
    
    def is_leap_year(self, year: int) -> bool:
        """Check if year is leap year."""
        return calendar.isleap(year)
    
    # Calendar Operations
    def start_of_day(self, dt: datetime) -> datetime:
        """Get start of day (00:00:00)."""
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def end_of_day(self, dt: datetime) -> datetime:
        """Get end of day (23:59:59.999999)."""
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    def start_of_week(self, dt: datetime, start_day: int = 0) -> datetime:
        """Get start of week (Monday by default)."""
        days_since_start = (dt.weekday() - start_day) % 7
        start_date = dt.date() - timedelta(days=days_since_start)
        return datetime.combine(start_date, dt.time().replace(hour=0, minute=0, second=0, microsecond=0))
    
    def end_of_week(self, dt: datetime, start_day: int = 0) -> datetime:
        """Get end of week."""
        start_of_week = self.start_of_week(dt, start_day)
        end_date = start_of_week.date() + timedelta(days=6)
        return datetime.combine(end_date, dt.time().replace(hour=23, minute=59, second=59, microsecond=999999))
    
    def start_of_month(self, dt: datetime) -> datetime:
        """Get start of month."""
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    def end_of_month(self, dt: datetime) -> datetime:
        """Get end of month."""
        next_month = dt.replace(day=28) + timedelta(days=4)
        last_day = next_month - timedelta(days=next_month.day)
        return last_day.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    def start_of_year(self, dt: datetime) -> datetime:
        """Get start of year."""
        return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    def end_of_year(self, dt: datetime) -> datetime:
        """Get end of year."""
        return dt.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    
    def days_in_month(self, year: int, month: int) -> int:
        """Get number of days in month."""
        return calendar.monthrange(year, month)[1]
    
    # Business Operations
    def add_business_days(self, dt: datetime, business_days: int, 
                         holidays: Optional[List[date]] = None) -> datetime:
        """Add business days (excluding weekends and holidays)."""
        if holidays is None:
            holidays = []
        
        current_date = dt.date()
        days_added = 0
        direction = 1 if business_days > 0 else -1
        target_days = abs(business_days)
        
        while days_added < target_days:
            current_date += timedelta(days=direction)
            
            # Skip weekends and holidays
            if (current_date.weekday() < 5 and current_date not in holidays):
                days_added += 1
        
        return datetime.combine(current_date, dt.time())
    
    def subtract_business_days(self, dt: datetime, business_days: int,
                              holidays: Optional[List[date]] = None) -> datetime:
        """Subtract business days."""
        return self.add_business_days(dt, -business_days, holidays)
    
    def count_business_days(self, start_dt: datetime, end_dt: datetime,
                           holidays: Optional[List[date]] = None) -> int:
        """Count business days between two dates."""
        if holidays is None:
            holidays = []
        
        start_date = min(start_dt.date(), end_dt.date())
        end_date = max(start_dt.date(), end_dt.date())
        
        business_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 5 and current_date not in holidays:
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
    
    def is_business_day(self, dt: datetime, holidays: Optional[List[date]] = None) -> bool:
        """Check if date is a business day."""
        if holidays is None:
            holidays = []
        
        return dt.weekday() < 5 and dt.date() not in holidays
    
    def next_business_day(self, dt: datetime, holidays: Optional[List[date]] = None) -> datetime:
        """Get next business day."""
        return self.add_business_days(dt, 1, holidays)
    
    def previous_business_day(self, dt: datetime, holidays: Optional[List[date]] = None) -> datetime:
        """Get previous business day."""
        return self.subtract_business_days(dt, 1, holidays)
    
    # Conversion Operations
    def to_timestamp(self, dt: datetime) -> float:
        """Convert datetime to timestamp."""
        return dt.timestamp()
    
    def from_timestamp(self, timestamp: float, timezone_str: Optional[str] = None) -> datetime:
        """Convert timestamp to datetime."""
        dt = datetime.fromtimestamp(timestamp, tz.UTC)
        
        if timezone_str:
            target_tz = tz.gettz(timezone_str)
            if target_tz:
                dt = dt.astimezone(target_tz)
        
        return dt
    
    def to_iso(self, dt: datetime) -> str:
        """Convert datetime to ISO format."""
        return dt.isoformat()
    
    def from_iso(self, iso_string: str) -> datetime:
        """Convert ISO string to datetime."""
        return datetime.fromisoformat(iso_string)
    
    def to_unix(self, dt: datetime) -> int:
        """Convert datetime to Unix timestamp."""
        return int(dt.timestamp())
    
    def from_unix(self, unix_timestamp: int, timezone_str: Optional[str] = None) -> datetime:
        """Convert Unix timestamp to datetime."""
        return self.from_timestamp(float(unix_timestamp), timezone_str)
    
    # Generation Operations
    def date_range(self, start_dt: datetime, end_dt: datetime, 
                  step_days: int = 1, include_end: bool = True) -> List[datetime]:
        """Generate range of dates."""
        dates = []
        current_dt = start_dt
        
        while current_dt < end_dt or (include_end and current_dt <= end_dt):
            dates.append(current_dt)
            current_dt += timedelta(days=step_days)
        
        return dates
    
    def recurring_dates(self, start_dt: datetime, rule_str: str, count: int = 10) -> List[datetime]:
        """Generate recurring dates using RRULE."""
        try:
            # Parse RRULE string
            rule = rrule.rrulestr(f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}\nRRULE:{rule_str}")
            return list(rule[:count])
        except Exception as e:
            raise DateTimeOperationsError(f"Invalid RRULE: {str(e)}")
    
    def working_days(self, start_dt: datetime, end_dt: datetime,
                    holidays: Optional[List[date]] = None) -> List[datetime]:
        """Generate list of working days between dates."""
        if holidays is None:
            holidays = []
        
        working_days = []
        current_dt = start_dt
        
        while current_dt <= end_dt:
            if self.is_business_day(current_dt, holidays):
                working_days.append(current_dt)
            current_dt += timedelta(days=1)
        
        return working_days
    
    # Validation Operations
    def is_valid_date(self, date_string: str, format_string: Optional[str] = None) -> bool:
        """Check if date string is valid."""
        try:
            self.parse(date_string, format_string)
            return True
        except:
            return False
    
    def validate_format(self, date_string: str, format_string: str) -> Dict[str, Any]:
        """Validate date string against specific format."""
        try:
            parsed_dt = datetime.strptime(date_string, format_string)
            return {
                "valid": True,
                "parsed_date": parsed_dt,
                "format": format_string
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "format": format_string
            }
    
    # Batch Operations
    def batch_parse(self, date_strings: List[str], format_string: Optional[str] = None,
                   timezone_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """Parse multiple date strings."""
        results = []
        
        for i, date_string in enumerate(date_strings):
            try:
                parsed_dt = self.parse(date_string, format_string, timezone_str)
                results.append({
                    'index': i,
                    'status': 'success',
                    'input': date_string,
                    'result': parsed_dt
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'status': 'error',
                    'input': date_string,
                    'error': str(e)
                })
        
        return results
    
    def batch_format(self, datetimes: List[datetime], format_string: str) -> List[Dict[str, Any]]:
        """Format multiple datetime objects."""
        results = []
        
        for i, dt in enumerate(datetimes):
            try:
                formatted = self.format(dt, format_string)
                results.append({
                    'index': i,
                    'status': 'success',
                    'input': dt,
                    'result': formatted
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'status': 'error',
                    'input': dt,
                    'error': str(e)
                })
        
        return results

class DateTimeNode(BaseNode):
    """
    Date/Time operations node for ACT workflow system.
    
    Provides comprehensive date and time operations including:
    - Parsing and formatting in various formats
    - Timezone conversions and management
    - Date arithmetic and calculations
    - Business day operations
    - Calendar utilities
    - Batch processing capabilities
    """
    
    # Operation metadata for validation and documentation
    OPERATION_METADATA = {
        DateTimeOperation.PARSE: {
            "required": ["date_string"],
            "optional": ["format_string", "timezone_str"],
            "description": "Parse date string into datetime object"
        },
        DateTimeOperation.FORMAT: {
            "required": ["datetime", "format_string"],
            "optional": [],
            "description": "Format datetime object as string"
        },
        DateTimeOperation.ADD_DAYS: {
            "required": ["datetime", "days"],
            "optional": [],
            "description": "Add days to datetime"
        },
        DateTimeOperation.DIFF_DAYS: {
            "required": ["datetime1", "datetime2"],
            "optional": [],
            "description": "Calculate difference in days"
        },
        DateTimeOperation.TO_TIMEZONE: {
            "required": ["datetime", "timezone"],
            "optional": [],
            "description": "Convert datetime to timezone"
        },
        DateTimeOperation.BATCH_PARSE: {
            "required": ["date_strings"],
            "optional": ["format_string", "timezone_str"],
            "description": "Parse multiple date strings"
        }
    }
    
    def __init__(self):
        super().__init__()
        self.datetime_processor = DateTimeProcessor()
        
        # Dispatch map for operations
        self.dispatch_map = {
            DateTimeOperation.PARSE: self._handle_parse,
            DateTimeOperation.FORMAT: self._handle_format,
            DateTimeOperation.NOW: self._handle_now,
            DateTimeOperation.TODAY: self._handle_today,
            DateTimeOperation.TOMORROW: self._handle_tomorrow,
            DateTimeOperation.YESTERDAY: self._handle_yesterday,
            
            DateTimeOperation.ADD_DAYS: self._handle_add_days,
            DateTimeOperation.ADD_WEEKS: self._handle_add_weeks,
            DateTimeOperation.ADD_MONTHS: self._handle_add_months,
            DateTimeOperation.ADD_YEARS: self._handle_add_years,
            DateTimeOperation.ADD_HOURS: self._handle_add_hours,
            DateTimeOperation.ADD_MINUTES: self._handle_add_minutes,
            DateTimeOperation.ADD_SECONDS: self._handle_add_seconds,
            
            DateTimeOperation.SUBTRACT_DAYS: self._handle_subtract_days,
            DateTimeOperation.SUBTRACT_WEEKS: self._handle_subtract_weeks,
            DateTimeOperation.SUBTRACT_MONTHS: self._handle_subtract_months,
            DateTimeOperation.SUBTRACT_YEARS: self._handle_subtract_years,
            DateTimeOperation.SUBTRACT_HOURS: self._handle_subtract_hours,
            DateTimeOperation.SUBTRACT_MINUTES: self._handle_subtract_minutes,
            DateTimeOperation.SUBTRACT_SECONDS: self._handle_subtract_seconds,
            
            DateTimeOperation.TO_TIMEZONE: self._handle_to_timezone,
            DateTimeOperation.FROM_TIMEZONE: self._handle_from_timezone,
            DateTimeOperation.LIST_TIMEZONES: self._handle_list_timezones,
            DateTimeOperation.GET_TIMEZONE_INFO: self._handle_get_timezone_info,
            
            DateTimeOperation.DIFF_DAYS: self._handle_diff_days,
            DateTimeOperation.DIFF_WEEKS: self._handle_diff_weeks,
            DateTimeOperation.DIFF_MONTHS: self._handle_diff_months,
            DateTimeOperation.DIFF_YEARS: self._handle_diff_years,
            DateTimeOperation.DIFF_HOURS: self._handle_diff_hours,
            DateTimeOperation.DIFF_MINUTES: self._handle_diff_minutes,
            DateTimeOperation.DIFF_SECONDS: self._handle_diff_seconds,
            DateTimeOperation.TIME_UNTIL: self._handle_time_until,
            DateTimeOperation.TIME_SINCE: self._handle_time_since,
            DateTimeOperation.AGE: self._handle_age,
            
            DateTimeOperation.GET_YEAR: self._handle_get_year,
            DateTimeOperation.GET_MONTH: self._handle_get_month,
            DateTimeOperation.GET_DAY: self._handle_get_day,
            DateTimeOperation.GET_HOUR: self._handle_get_hour,
            DateTimeOperation.GET_MINUTE: self._handle_get_minute,
            DateTimeOperation.GET_SECOND: self._handle_get_second,
            DateTimeOperation.GET_WEEKDAY: self._handle_get_weekday,
            DateTimeOperation.GET_QUARTER: self._handle_get_quarter,
            DateTimeOperation.GET_WEEK_NUMBER: self._handle_get_week_number,
            DateTimeOperation.GET_DAY_OF_YEAR: self._handle_get_day_of_year,
            
            DateTimeOperation.IS_BEFORE: self._handle_is_before,
            DateTimeOperation.IS_AFTER: self._handle_is_after,
            DateTimeOperation.IS_SAME: self._handle_is_same,
            DateTimeOperation.IS_BETWEEN: self._handle_is_between,
            DateTimeOperation.IS_WEEKEND: self._handle_is_weekend,
            DateTimeOperation.IS_WEEKDAY: self._handle_is_weekday,
            DateTimeOperation.IS_LEAP_YEAR: self._handle_is_leap_year,
            
            DateTimeOperation.START_OF_DAY: self._handle_start_of_day,
            DateTimeOperation.END_OF_DAY: self._handle_end_of_day,
            DateTimeOperation.START_OF_WEEK: self._handle_start_of_week,
            DateTimeOperation.END_OF_WEEK: self._handle_end_of_week,
            DateTimeOperation.START_OF_MONTH: self._handle_start_of_month,
            DateTimeOperation.END_OF_MONTH: self._handle_end_of_month,
            DateTimeOperation.START_OF_YEAR: self._handle_start_of_year,
            DateTimeOperation.END_OF_YEAR: self._handle_end_of_year,
            DateTimeOperation.DAYS_IN_MONTH: self._handle_days_in_month,
            
            DateTimeOperation.ADD_BUSINESS_DAYS: self._handle_add_business_days,
            DateTimeOperation.SUBTRACT_BUSINESS_DAYS: self._handle_subtract_business_days,
            DateTimeOperation.COUNT_BUSINESS_DAYS: self._handle_count_business_days,
            DateTimeOperation.IS_BUSINESS_DAY: self._handle_is_business_day,
            DateTimeOperation.NEXT_BUSINESS_DAY: self._handle_next_business_day,
            DateTimeOperation.PREVIOUS_BUSINESS_DAY: self._handle_previous_business_day,
            
            DateTimeOperation.TO_TIMESTAMP: self._handle_to_timestamp,
            DateTimeOperation.FROM_TIMESTAMP: self._handle_from_timestamp,
            DateTimeOperation.TO_ISO: self._handle_to_iso,
            DateTimeOperation.FROM_ISO: self._handle_from_iso,
            DateTimeOperation.TO_UNIX: self._handle_to_unix,
            DateTimeOperation.FROM_UNIX: self._handle_from_unix,
            
            DateTimeOperation.DATE_RANGE: self._handle_date_range,
            DateTimeOperation.RECURRING_DATES: self._handle_recurring_dates,
            DateTimeOperation.WORKING_DAYS: self._handle_working_days,
            
            DateTimeOperation.IS_VALID_DATE: self._handle_is_valid_date,
            DateTimeOperation.VALIDATE_FORMAT: self._handle_validate_format,
            
            DateTimeOperation.BATCH_PARSE: self._handle_batch_parse,
            DateTimeOperation.BATCH_FORMAT: self._handle_batch_format,
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for date/time operations."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [op.value for op in DateTimeOperation],
                    "description": "Date/time operation to perform"
                },
                # Basic parameters
                "datetime": {
                    "type": "string",
                    "description": "Datetime string or ISO format"
                },
                "datetime1": {
                    "type": "string",
                    "description": "First datetime"
                },
                "datetime2": {
                    "type": "string",
                    "description": "Second datetime"
                },
                "date_string": {
                    "type": "string",
                    "description": "Date string to parse"
                },
                "date_strings": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of date strings"
                },
                "datetimes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of datetime strings"
                },
                "format_string": {
                    "type": "string",
                    "description": "Format string for parsing/formatting"
                },
                # Arithmetic parameters
                "days": {
                    "type": "integer",
                    "description": "Number of days"
                },
                "weeks": {
                    "type": "integer",
                    "description": "Number of weeks"
                },
                "months": {
                    "type": "integer",
                    "description": "Number of months"
                },
                "years": {
                    "type": "integer",
                    "description": "Number of years"
                },
                "hours": {
                    "type": "integer",
                    "description": "Number of hours"
                },
                "minutes": {
                    "type": "integer",
                    "description": "Number of minutes"
                },
                "seconds": {
                    "type": "integer",
                    "description": "Number of seconds"
                },
                "business_days": {
                    "type": "integer",
                    "description": "Number of business days"
                },
                # Timezone parameters
                "timezone": {
                    "type": "string",
                    "description": "Timezone identifier"
                },
                "timezone_str": {
                    "type": "string",
                    "description": "Timezone string"
                },
                "source_timezone": {
                    "type": "string",
                    "description": "Source timezone"
                },
                "target_timezone": {
                    "type": "string",
                    "description": "Target timezone"
                },
                "region": {
                    "type": "string",
                    "description": "Timezone region filter"
                },
                # Comparison parameters
                "precision": {
                    "type": "string",
                    "enum": ["year", "month", "day", "hour", "minute", "second"],
                    "description": "Precision for comparison"
                },
                "inclusive": {
                    "type": "boolean",
                    "description": "Include endpoints in range"
                },
                # Calendar parameters
                "start_day": {
                    "type": "integer",
                    "description": "Start day of week (0=Monday)"
                },
                "year": {
                    "type": "integer",
                    "description": "Year"
                },
                "month": {
                    "type": "integer",
                    "description": "Month"
                },
                # Generation parameters
                "start_dt": {
                    "type": "string",
                    "description": "Start datetime"
                },
                "end_dt": {
                    "type": "string",
                    "description": "End datetime"
                },
                "step_days": {
                    "type": "integer",
                    "description": "Step in days"
                },
                "include_end": {
                    "type": "boolean",
                    "description": "Include end date in range"
                },
                "rule_str": {
                    "type": "string",
                    "description": "RRULE string for recurring dates"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of occurrences"
                },
                "holidays": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of holiday dates"
                },
                # Conversion parameters
                "timestamp": {
                    "type": "number",
                    "description": "Timestamp value"
                },
                "unix_timestamp": {
                    "type": "integer",
                    "description": "Unix timestamp"
                },
                "iso_string": {
                    "type": "string",
                    "description": "ISO datetime string"
                },
                # Other parameters
                "birth_date": {
                    "type": "string",
                    "description": "Birth date for age calculation"
                },
                "reference_date": {
                    "type": "string",
                    "description": "Reference date"
                },
                "target_dt": {
                    "type": "string",
                    "description": "Target datetime"
                },
                "from_dt": {
                    "type": "string",
                    "description": "From datetime"
                },
                "past_dt": {
                    "type": "string",
                    "description": "Past datetime"
                }
            },
            "required": ["operation"],
            "additionalProperties": True
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute date/time operation."""
        try:
            # Validate parameters
            validation_result = self.validate_params(params)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "error": f"Parameter validation failed: {validation_result['error']}"
                }
            
            operation = DateTimeOperation(params["operation"])
            
            logger.info(f"Executing date/time operation: {operation}")
            
            # Get operation handler
            handler = self.dispatch_map.get(operation)
            if not handler:
                return {
                    "status": "error",
                    "error": f"Operation {operation} not implemented"
                }
            
            # Execute operation
            start_time = time.time()
            result = await handler(params)
            end_time = time.time()
            
            logger.info(f"Date/time operation {operation} completed successfully")
            
            return {
                "status": "success",
                "operation": operation,
                "result": result,
                "processing_time": round(end_time - start_time, 6),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Date/time operation error: {str(e)}")
            return {
                "status": "error",
                "error": f"Date/time operation error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation parameters."""
        try:
            operation = params.get("operation")
            if not operation:
                return {"valid": False, "error": "Operation is required"}
            
            if operation not in [op.value for op in DateTimeOperation]:
                return {"valid": False, "error": f"Invalid operation: {operation}"}
            
            # Get operation metadata
            metadata = self.OPERATION_METADATA.get(DateTimeOperation(operation))
            if metadata:
                # Check required parameters
                for param in metadata["required"]:
                    if param not in params:
                        return {"valid": False, "error": f"Required parameter missing: {param}"}
                
                # Validate specific parameters
                if operation == DateTimeOperation.BATCH_PARSE:
                    date_strings = params.get("date_strings", [])
                    if not isinstance(date_strings, list) or len(date_strings) == 0:
                        return {"valid": False, "error": "date_strings must be a non-empty list"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def _parse_datetime(self, dt_str: str) -> datetime:
        """Helper to parse datetime string."""
        if isinstance(dt_str, datetime):
            return dt_str
        return self.datetime_processor.parse(dt_str)
    
    # Parsing and Formatting Handlers
    async def _handle_parse(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parse operation."""
        date_string = params["date_string"]
        format_string = params.get("format_string")
        timezone_str = params.get("timezone_str")
        
        result = self.datetime_processor.parse(date_string, format_string, timezone_str)
        
        return {
            "result": result.isoformat(),
            "datetime_object": result,
            "input": date_string,
            "format": format_string,
            "timezone": timezone_str
        }
    
    async def _handle_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle format operation."""
        dt = self._parse_datetime(params["datetime"])
        format_string = params["format_string"]
        
        result = self.datetime_processor.format(dt, format_string)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "format": format_string
        }
    
    async def _handle_now(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle now operation."""
        timezone_str = params.get("timezone_str")
        
        result = self.datetime_processor.now(timezone_str)
        
        return {
            "result": result.isoformat(),
            "datetime_object": result,
            "timezone": timezone_str
        }
    
    async def _handle_today(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle today operation."""
        timezone_str = params.get("timezone_str")
        
        result = self.datetime_processor.today(timezone_str)
        
        return {
            "result": result.isoformat(),
            "date_object": result,
            "timezone": timezone_str
        }
    
    async def _handle_tomorrow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tomorrow operation."""
        timezone_str = params.get("timezone_str")
        
        result = self.datetime_processor.tomorrow(timezone_str)
        
        return {
            "result": result.isoformat(),
            "date_object": result,
            "timezone": timezone_str
        }
    
    async def _handle_yesterday(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle yesterday operation."""
        timezone_str = params.get("timezone_str")
        
        result = self.datetime_processor.yesterday(timezone_str)
        
        return {
            "result": result.isoformat(),
            "date_object": result,
            "timezone": timezone_str
        }
    
    # Addition Handlers
    async def _handle_add_days(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add days operation."""
        dt = self._parse_datetime(params["datetime"])
        days = params["days"]
        
        result = self.datetime_processor.add_days(dt, days)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "days_added": days,
            "operation": "add_days"
        }
    
    async def _handle_add_weeks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add weeks operation."""
        dt = self._parse_datetime(params["datetime"])
        weeks = params["weeks"]
        
        result = self.datetime_processor.add_weeks(dt, weeks)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "weeks_added": weeks,
            "operation": "add_weeks"
        }
    
    async def _handle_add_months(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add months operation."""
        dt = self._parse_datetime(params["datetime"])
        months = params["months"]
        
        result = self.datetime_processor.add_months(dt, months)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "months_added": months,
            "operation": "add_months"
        }
    
    async def _handle_add_years(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add years operation."""
        dt = self._parse_datetime(params["datetime"])
        years = params["years"]
        
        result = self.datetime_processor.add_years(dt, years)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "years_added": years,
            "operation": "add_years"
        }
    
    async def _handle_add_hours(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add hours operation."""
        dt = self._parse_datetime(params["datetime"])
        hours = params["hours"]
        
        result = self.datetime_processor.add_hours(dt, hours)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "hours_added": hours,
            "operation": "add_hours"
        }
    
    async def _handle_add_minutes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add minutes operation."""
        dt = self._parse_datetime(params["datetime"])
        minutes = params["minutes"]
        
        result = self.datetime_processor.add_minutes(dt, minutes)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "minutes_added": minutes,
            "operation": "add_minutes"
        }
    
    async def _handle_add_seconds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add seconds operation."""
        dt = self._parse_datetime(params["datetime"])
        seconds = params["seconds"]
        
        result = self.datetime_processor.add_seconds(dt, seconds)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "seconds_added": seconds,
            "operation": "add_seconds"
        }
    
    # Subtraction Handlers (similar pattern, abbreviated for space)
    async def _handle_subtract_days(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subtract days operation."""
        dt = self._parse_datetime(params["datetime"])
        days = params["days"]
        
        result = self.datetime_processor.subtract_days(dt, days)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "days_subtracted": days,
            "operation": "subtract_days"
        }
    
    async def _handle_subtract_weeks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subtract weeks operation."""
        dt = self._parse_datetime(params["datetime"])
        weeks = params["weeks"]
        
        result = self.datetime_processor.subtract_weeks(dt, weeks)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "weeks_subtracted": weeks,
            "operation": "subtract_weeks"
        }
    
    async def _handle_subtract_months(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subtract months operation."""
        dt = self._parse_datetime(params["datetime"])
        months = params["months"]
        
        result = self.datetime_processor.subtract_months(dt, months)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "months_subtracted": months,
            "operation": "subtract_months"
        }
    
    async def _handle_subtract_years(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subtract years operation."""
        dt = self._parse_datetime(params["datetime"])
        years = params["years"]
        
        result = self.datetime_processor.subtract_years(dt, years)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "years_subtracted": years,
            "operation": "subtract_years"
        }
    
    async def _handle_subtract_hours(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subtract hours operation."""
        dt = self._parse_datetime(params["datetime"])
        hours = params["hours"]
        
        result = self.datetime_processor.subtract_hours(dt, hours)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "hours_subtracted": hours,
            "operation": "subtract_hours"
        }
    
    async def _handle_subtract_minutes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subtract minutes operation."""
        dt = self._parse_datetime(params["datetime"])
        minutes = params["minutes"]
        
        result = self.datetime_processor.subtract_minutes(dt, minutes)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "minutes_subtracted": minutes,
            "operation": "subtract_minutes"
        }
    
    async def _handle_subtract_seconds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subtract seconds operation."""
        dt = self._parse_datetime(params["datetime"])
        seconds = params["seconds"]
        
        result = self.datetime_processor.subtract_seconds(dt, seconds)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "seconds_subtracted": seconds,
            "operation": "subtract_seconds"
        }
    
    # Timezone Handlers
    async def _handle_to_timezone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timezone conversion."""
        dt = self._parse_datetime(params["datetime"])
        timezone_str = params["timezone"]
        
        result = self.datetime_processor.to_timezone(dt, timezone_str)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "timezone": timezone_str,
            "operation": "timezone_conversion"
        }
    
    async def _handle_from_timezone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timezone conversion from source to target."""
        dt = self._parse_datetime(params["datetime"])
        source_timezone = params["source_timezone"]
        target_timezone = params.get("target_timezone", "UTC")
        
        result = self.datetime_processor.from_timezone(dt, source_timezone, target_timezone)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "source_timezone": source_timezone,
            "target_timezone": target_timezone,
            "operation": "timezone_conversion"
        }
    
    async def _handle_list_timezones(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list timezones operation."""
        region = params.get("region")
        
        result = self.datetime_processor.list_timezones(region)
        
        return {
            "result": result,
            "count": len(result),
            "region": region,
            "operation": "list_timezones"
        }
    
    async def _handle_get_timezone_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get timezone info operation."""
        timezone_str = params["timezone"]
        dt = None
        if "datetime" in params:
            dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.get_timezone_info(timezone_str, dt)
        
        return {
            "result": result,
            "timezone": timezone_str,
            "reference_datetime": dt.isoformat() if dt else None,
            "operation": "timezone_info"
        }
    
    # Difference Calculation Handlers
    async def _handle_diff_days(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle days difference calculation."""
        dt1 = self._parse_datetime(params["datetime1"])
        dt2 = self._parse_datetime(params["datetime2"])
        
        result = self.datetime_processor.diff_days(dt1, dt2)
        
        return {
            "result": result,
            "datetime1": dt1.isoformat(),
            "datetime2": dt2.isoformat(),
            "unit": "days",
            "operation": "difference_calculation"
        }
    
    async def _handle_diff_weeks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle weeks difference calculation."""
        dt1 = self._parse_datetime(params["datetime1"])
        dt2 = self._parse_datetime(params["datetime2"])
        
        result = self.datetime_processor.diff_weeks(dt1, dt2)
        
        return {
            "result": result,
            "datetime1": dt1.isoformat(),
            "datetime2": dt2.isoformat(),
            "unit": "weeks",
            "operation": "difference_calculation"
        }
    
    async def _handle_diff_months(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle months difference calculation."""
        dt1 = self._parse_datetime(params["datetime1"])
        dt2 = self._parse_datetime(params["datetime2"])
        
        result = self.datetime_processor.diff_months(dt1, dt2)
        
        return {
            "result": result,
            "datetime1": dt1.isoformat(),
            "datetime2": dt2.isoformat(),
            "unit": "months",
            "operation": "difference_calculation"
        }
    
    async def _handle_diff_years(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle years difference calculation."""
        dt1 = self._parse_datetime(params["datetime1"])
        dt2 = self._parse_datetime(params["datetime2"])
        
        result = self.datetime_processor.diff_years(dt1, dt2)
        
        return {
            "result": result,
            "datetime1": dt1.isoformat(),
            "datetime2": dt2.isoformat(),
            "unit": "years",
            "operation": "difference_calculation"
        }
    
    async def _handle_diff_hours(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hours difference calculation."""
        dt1 = self._parse_datetime(params["datetime1"])
        dt2 = self._parse_datetime(params["datetime2"])
        
        result = self.datetime_processor.diff_hours(dt1, dt2)
        
        return {
            "result": result,
            "datetime1": dt1.isoformat(),
            "datetime2": dt2.isoformat(),
            "unit": "hours",
            "operation": "difference_calculation"
        }
    
    async def _handle_diff_minutes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle minutes difference calculation."""
        dt1 = self._parse_datetime(params["datetime1"])
        dt2 = self._parse_datetime(params["datetime2"])
        
        result = self.datetime_processor.diff_minutes(dt1, dt2)
        
        return {
            "result": result,
            "datetime1": dt1.isoformat(),
            "datetime2": dt2.isoformat(),
            "unit": "minutes",
            "operation": "difference_calculation"
        }
    
    async def _handle_diff_seconds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle seconds difference calculation."""
        dt1 = self._parse_datetime(params["datetime1"])
        dt2 = self._parse_datetime(params["datetime2"])
        
        result = self.datetime_processor.diff_seconds(dt1, dt2)
        
        return {
            "result": result,
            "datetime1": dt1.isoformat(),
            "datetime2": dt2.isoformat(),
            "unit": "seconds",
            "operation": "difference_calculation"
        }
    
    async def _handle_time_until(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle time until calculation."""
        target_dt = self._parse_datetime(params["target_dt"])
        from_dt = None
        if "from_dt" in params:
            from_dt = self._parse_datetime(params["from_dt"])
        
        result = self.datetime_processor.time_until(target_dt, from_dt)
        
        return {
            "result": result,
            "target_datetime": target_dt.isoformat(),
            "from_datetime": from_dt.isoformat() if from_dt else None,
            "operation": "time_until"
        }
    
    async def _handle_time_since(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle time since calculation."""
        past_dt = self._parse_datetime(params["past_dt"])
        from_dt = None
        if "from_dt" in params:
            from_dt = self._parse_datetime(params["from_dt"])
        
        result = self.datetime_processor.time_since(past_dt, from_dt)
        
        return {
            "result": result,
            "past_datetime": past_dt.isoformat(),
            "from_datetime": from_dt.isoformat() if from_dt else None,
            "operation": "time_since"
        }
    
    async def _handle_age(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle age calculation."""
        birth_date = self._parse_datetime(params["birth_date"])
        reference_date = None
        if "reference_date" in params:
            reference_date = self._parse_datetime(params["reference_date"])
        
        result = self.datetime_processor.age(birth_date, reference_date)
        
        return {
            "result": result,
            "birth_date": birth_date.isoformat(),
            "reference_date": reference_date.isoformat() if reference_date else None,
            "operation": "age_calculation"
        }
    
    # Extraction Handlers
    async def _handle_get_year(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get year operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.get_year(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "component": "year"
        }
    
    async def _handle_get_month(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get month operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.get_month(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "component": "month"
        }
    
    async def _handle_get_day(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get day operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.get_day(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "component": "day"
        }
    
    async def _handle_get_hour(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get hour operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.get_hour(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "component": "hour"
        }
    
    async def _handle_get_minute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get minute operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.get_minute(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "component": "minute"
        }
    
    async def _handle_get_second(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get second operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.get_second(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "component": "second"
        }
    
    async def _handle_get_weekday(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get weekday operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.get_weekday(dt)
        
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        return {
            "result": result,
            "weekday_name": weekday_names[result],
            "datetime": dt.isoformat(),
            "component": "weekday"
        }
    
    async def _handle_get_quarter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get quarter operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.get_quarter(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "component": "quarter"
        }
    
    async def _handle_get_week_number(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get week number operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.get_week_number(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "component": "week_number"
        }
    
    async def _handle_get_day_of_year(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get day of year operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.get_day_of_year(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "component": "day_of_year"
        }
    
    # Comparison Handlers
    async def _handle_is_before(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is before comparison."""
        dt1 = self._parse_datetime(params["datetime1"])
        dt2 = self._parse_datetime(params["datetime2"])
        
        result = self.datetime_processor.is_before(dt1, dt2)
        
        return {
            "result": result,
            "datetime1": dt1.isoformat(),
            "datetime2": dt2.isoformat(),
            "comparison": "is_before"
        }
    
    async def _handle_is_after(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is after comparison."""
        dt1 = self._parse_datetime(params["datetime1"])
        dt2 = self._parse_datetime(params["datetime2"])
        
        result = self.datetime_processor.is_after(dt1, dt2)
        
        return {
            "result": result,
            "datetime1": dt1.isoformat(),
            "datetime2": dt2.isoformat(),
            "comparison": "is_after"
        }
    
    async def _handle_is_same(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is same comparison."""
        dt1 = self._parse_datetime(params["datetime1"])
        dt2 = self._parse_datetime(params["datetime2"])
        precision = params.get("precision", "second")
        
        result = self.datetime_processor.is_same(dt1, dt2, precision)
        
        return {
            "result": result,
            "datetime1": dt1.isoformat(),
            "datetime2": dt2.isoformat(),
            "precision": precision,
            "comparison": "is_same"
        }
    
    async def _handle_is_between(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is between comparison."""
        dt = self._parse_datetime(params["datetime"])
        start_dt = self._parse_datetime(params["start_dt"])
        end_dt = self._parse_datetime(params["end_dt"])
        inclusive = params.get("inclusive", True)
        
        result = self.datetime_processor.is_between(dt, start_dt, end_dt, inclusive)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "start_datetime": start_dt.isoformat(),
            "end_datetime": end_dt.isoformat(),
            "inclusive": inclusive,
            "comparison": "is_between"
        }
    
    async def _handle_is_weekend(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is weekend check."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.is_weekend(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "weekday": dt.weekday(),
            "check": "is_weekend"
        }
    
    async def _handle_is_weekday(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is weekday check."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.is_weekday(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "weekday": dt.weekday(),
            "check": "is_weekday"
        }
    
    async def _handle_is_leap_year(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is leap year check."""
        year = params["year"]
        
        result = self.datetime_processor.is_leap_year(year)
        
        return {
            "result": result,
            "year": year,
            "check": "is_leap_year"
        }
    
    # Calendar Operation Handlers
    async def _handle_start_of_day(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle start of day operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.start_of_day(dt)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "operation": "start_of_day"
        }
    
    async def _handle_end_of_day(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle end of day operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.end_of_day(dt)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "operation": "end_of_day"
        }
    
    async def _handle_start_of_week(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle start of week operation."""
        dt = self._parse_datetime(params["datetime"])
        start_day = params.get("start_day", 0)
        
        result = self.datetime_processor.start_of_week(dt, start_day)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "start_day": start_day,
            "operation": "start_of_week"
        }
    
    async def _handle_end_of_week(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle end of week operation."""
        dt = self._parse_datetime(params["datetime"])
        start_day = params.get("start_day", 0)
        
        result = self.datetime_processor.end_of_week(dt, start_day)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "start_day": start_day,
            "operation": "end_of_week"
        }
    
    async def _handle_start_of_month(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle start of month operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.start_of_month(dt)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "operation": "start_of_month"
        }
    
    async def _handle_end_of_month(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle end of month operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.end_of_month(dt)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "operation": "end_of_month"
        }
    
    async def _handle_start_of_year(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle start of year operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.start_of_year(dt)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "operation": "start_of_year"
        }
    
    async def _handle_end_of_year(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle end of year operation."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.end_of_year(dt)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "operation": "end_of_year"
        }
    
    async def _handle_days_in_month(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle days in month operation."""
        year = params["year"]
        month = params["month"]
        
        result = self.datetime_processor.days_in_month(year, month)
        
        return {
            "result": result,
            "year": year,
            "month": month,
            "operation": "days_in_month"
        }
    
    # Business Operation Handlers
    async def _handle_add_business_days(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add business days operation."""
        dt = self._parse_datetime(params["datetime"])
        business_days = params["business_days"]
        holidays = []
        if "holidays" in params:
            holidays = [self._parse_datetime(h).date() for h in params["holidays"]]
        
        result = self.datetime_processor.add_business_days(dt, business_days, holidays)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "business_days_added": business_days,
            "holidays_count": len(holidays),
            "operation": "add_business_days"
        }
    
    async def _handle_subtract_business_days(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subtract business days operation."""
        dt = self._parse_datetime(params["datetime"])
        business_days = params["business_days"]
        holidays = []
        if "holidays" in params:
            holidays = [self._parse_datetime(h).date() for h in params["holidays"]]
        
        result = self.datetime_processor.subtract_business_days(dt, business_days, holidays)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "business_days_subtracted": business_days,
            "holidays_count": len(holidays),
            "operation": "subtract_business_days"
        }
    
    async def _handle_count_business_days(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle count business days operation."""
        start_dt = self._parse_datetime(params["start_dt"])
        end_dt = self._parse_datetime(params["end_dt"])
        holidays = []
        if "holidays" in params:
            holidays = [self._parse_datetime(h).date() for h in params["holidays"]]
        
        result = self.datetime_processor.count_business_days(start_dt, end_dt, holidays)
        
        return {
            "result": result,
            "start_datetime": start_dt.isoformat(),
            "end_datetime": end_dt.isoformat(),
            "holidays_count": len(holidays),
            "operation": "count_business_days"
        }
    
    async def _handle_is_business_day(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is business day check."""
        dt = self._parse_datetime(params["datetime"])
        holidays = []
        if "holidays" in params:
            holidays = [self._parse_datetime(h).date() for h in params["holidays"]]
        
        result = self.datetime_processor.is_business_day(dt, holidays)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "weekday": dt.weekday(),
            "holidays_count": len(holidays),
            "check": "is_business_day"
        }
    
    async def _handle_next_business_day(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle next business day operation."""
        dt = self._parse_datetime(params["datetime"])
        holidays = []
        if "holidays" in params:
            holidays = [self._parse_datetime(h).date() for h in params["holidays"]]
        
        result = self.datetime_processor.next_business_day(dt, holidays)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "holidays_count": len(holidays),
            "operation": "next_business_day"
        }
    
    async def _handle_previous_business_day(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle previous business day operation."""
        dt = self._parse_datetime(params["datetime"])
        holidays = []
        if "holidays" in params:
            holidays = [self._parse_datetime(h).date() for h in params["holidays"]]
        
        result = self.datetime_processor.previous_business_day(dt, holidays)
        
        return {
            "result": result.isoformat(),
            "original": dt.isoformat(),
            "holidays_count": len(holidays),
            "operation": "previous_business_day"
        }
    
    # Conversion Operation Handlers
    async def _handle_to_timestamp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle to timestamp conversion."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.to_timestamp(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "operation": "to_timestamp"
        }
    
    async def _handle_from_timestamp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle from timestamp conversion."""
        timestamp = params["timestamp"]
        timezone_str = params.get("timezone_str")
        
        result = self.datetime_processor.from_timestamp(timestamp, timezone_str)
        
        return {
            "result": result.isoformat(),
            "timestamp": timestamp,
            "timezone": timezone_str,
            "operation": "from_timestamp"
        }
    
    async def _handle_to_iso(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle to ISO conversion."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.to_iso(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "operation": "to_iso"
        }
    
    async def _handle_from_iso(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle from ISO conversion."""
        iso_string = params["iso_string"]
        
        result = self.datetime_processor.from_iso(iso_string)
        
        return {
            "result": result.isoformat(),
            "iso_string": iso_string,
            "operation": "from_iso"
        }
    
    async def _handle_to_unix(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle to Unix timestamp conversion."""
        dt = self._parse_datetime(params["datetime"])
        
        result = self.datetime_processor.to_unix(dt)
        
        return {
            "result": result,
            "datetime": dt.isoformat(),
            "operation": "to_unix"
        }
    
    async def _handle_from_unix(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle from Unix timestamp conversion."""
        unix_timestamp = params["unix_timestamp"]
        timezone_str = params.get("timezone_str")
        
        result = self.datetime_processor.from_unix(unix_timestamp, timezone_str)
        
        return {
            "result": result.isoformat(),
            "unix_timestamp": unix_timestamp,
            "timezone": timezone_str,
            "operation": "from_unix"
        }
    
    # Generation Operation Handlers
    async def _handle_date_range(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle date range generation."""
        start_dt = self._parse_datetime(params["start_dt"])
        end_dt = self._parse_datetime(params["end_dt"])
        step_days = params.get("step_days", 1)
        include_end = params.get("include_end", True)
        
        result = self.datetime_processor.date_range(start_dt, end_dt, step_days, include_end)
        result_iso = [dt.isoformat() for dt in result]
        
        return {
            "result": result_iso,
            "start_datetime": start_dt.isoformat(),
            "end_datetime": end_dt.isoformat(),
            "step_days": step_days,
            "include_end": include_end,
            "count": len(result),
            "operation": "date_range"
        }
    
    async def _handle_recurring_dates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle recurring dates generation."""
        start_dt = self._parse_datetime(params["start_dt"])
        rule_str = params["rule_str"]
        count = params.get("count", 10)
        
        result = self.datetime_processor.recurring_dates(start_dt, rule_str, count)
        result_iso = [dt.isoformat() for dt in result]
        
        return {
            "result": result_iso,
            "start_datetime": start_dt.isoformat(),
            "rule": rule_str,
            "requested_count": count,
            "actual_count": len(result),
            "operation": "recurring_dates"
        }
    
    async def _handle_working_days(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle working days generation."""
        start_dt = self._parse_datetime(params["start_dt"])
        end_dt = self._parse_datetime(params["end_dt"])
        holidays = []
        if "holidays" in params:
            holidays = [self._parse_datetime(h).date() for h in params["holidays"]]
        
        result = self.datetime_processor.working_days(start_dt, end_dt, holidays)
        result_iso = [dt.isoformat() for dt in result]
        
        return {
            "result": result_iso,
            "start_datetime": start_dt.isoformat(),
            "end_datetime": end_dt.isoformat(),
            "holidays_count": len(holidays),
            "working_days_count": len(result),
            "operation": "working_days"
        }
    
    # Validation Operation Handlers
    async def _handle_is_valid_date(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle date validation."""
        date_string = params["date_string"]
        format_string = params.get("format_string")
        
        result = self.datetime_processor.is_valid_date(date_string, format_string)
        
        return {
            "result": result,
            "date_string": date_string,
            "format": format_string,
            "operation": "date_validation"
        }
    
    async def _handle_validate_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle format validation."""
        date_string = params["date_string"]
        format_string = params["format_string"]
        
        result = self.datetime_processor.validate_format(date_string, format_string)
        
        return {
            "result": result,
            "date_string": date_string,
            "format": format_string,
            "operation": "format_validation"
        }
    
    # Batch Operation Handlers
    async def _handle_batch_parse(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch parse operation."""
        date_strings = params["date_strings"]
        format_string = params.get("format_string")
        timezone_str = params.get("timezone_str")
        
        start_time = time.time()
        results = self.datetime_processor.batch_parse(date_strings, format_string, timezone_str)
        end_time = time.time()
        
        # Convert datetime objects to ISO strings for JSON serialization
        for result in results:
            if result['status'] == 'success' and isinstance(result['result'], datetime):
                result['result'] = result['result'].isoformat()
        
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        return {
            "results": results,
            "total_items": len(date_strings),
            "successful": successful,
            "failed": failed,
            "format": format_string,
            "timezone": timezone_str,
            "processing_time": round(end_time - start_time, 6),
            "rate": round(len(date_strings) / (end_time - start_time), 2) if end_time > start_time else 0
        }
    
    async def _handle_batch_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch format operation."""
        datetimes = [self._parse_datetime(dt) for dt in params["datetimes"]]
        format_string = params["format_string"]
        
        start_time = time.time()
        results = self.datetime_processor.batch_format(datetimes, format_string)
        end_time = time.time()
        
        # Convert datetime objects to ISO strings for JSON serialization
        for result in results:
            if result['status'] == 'success' and isinstance(result['input'], datetime):
                result['input'] = result['input'].isoformat()
        
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        return {
            "results": results,
            "total_items": len(datetimes),
            "successful": successful,
            "failed": failed,
            "format": format_string,
            "processing_time": round(end_time - start_time, 6),
            "rate": round(len(datetimes) / (end_time - start_time), 2) if end_time > start_time else 0
        }