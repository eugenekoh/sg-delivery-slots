import time
import click
import schedule
from slot_tracker import SlotTracker


@click.command()
@click.argument("postal_code")
@click.argument("rate")
@click.option("--api_token", "-a", envvar="API_TOKEN", help="pushover api token")
@click.option("--user_key", "-u", envvar="USER_KEY", help="pushover user key")
def main(postal_code, rate, api_token, user_key):
    """This function checks supermarket for the given POSTAL_CODE at a speed given by RATE in minutes."""

    if not api_token:
        raise Exception('API_TOKEN not found')
    elif not user_key:
        raise Exception('USER_KEY not found')

    st = SlotTracker(postal_code, api_token, user_key)
    st.check_slots()

    rate = int(rate)
    schedule.every(rate).minutes.do(st.check_slots)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
