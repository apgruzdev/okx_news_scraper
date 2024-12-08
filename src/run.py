import argparse
import datetime
import os
from pipeline import compose_news_pipeline
from config import LOGGER


def main():
    parser = argparse.ArgumentParser(description="Run the news pipeline and save output to a JSON file.")
    parser.add_argument("start_date", type=str, help="Start date in YYYY-MM-DD format")
    parser.add_argument("end_date", type=str, help="End date in YYYY-MM-DD format")
    parser.add_argument("folder", type=str, help="Folder to save the output JSON file")

    args = parser.parse_args()
    start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d").date()

    LOGGER.info(f"Starting news pipeline from {start_date} to {end_date}")

    json_output = compose_news_pipeline(start_date=start_date, end_date=end_date, 
                                        max_pages=2)

    # Create the output file name
    output_filename = f"news_{args.start_date}_to_{args.end_date}.json"
    output_path = os.path.join(args.folder, output_filename)

    os.makedirs(args.folder, exist_ok=True)

    # Write the JSON output to the file
    with open(output_path, "w") as f:
        f.write(json_output)

    LOGGER.info(f"Output saved to {output_path}")


if __name__ == "__main__":
    LOGGER.info("Script started")
    main()
    LOGGER.info("Script finished") 