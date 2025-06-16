# Datei: client/receiver.py

import asyncio
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import httpx # change: Added for async HTTP requests
from pydicom import Dataset
from scp import ModalityStoreSCP


class SeriesCollector:
    """A Series Collector is used to build up a list of instances (a DICOM series) as they are received by the modality.
    It stores the (during collection incomplete) series, the Series (Instance) UID, the time the series was last updated
    with a new instance and the information whether the dispatch of the series was started.
    """
    def __init__(self, first_dataset: Dataset) -> None:
        """Initialization of the Series Collector with the first dataset (instance).

        Args:
            first_dataset (Dataset): The first dataset or the regarding series received from the modality.
        """
        self.series_instance_uid = first_dataset.SeriesInstanceUID
        self.series: list[Dataset] = [first_dataset]
        self.last_update_time = time.time()
        self.dispatch_started = False

    def add_instance(self, dataset: Dataset) -> bool:
        """Add an dataset to the series collected by this Series Collector if it has the correct Series UID.

        Args:
            dataset (Dataset): The dataset to add.

        Returns:
            bool: `True`, if the Series UID of the dataset to add matched and the dataset was therefore added, `False` otherwise.
        """
        if self.series_instance_uid == dataset.SeriesInstanceUID:
            self.series.append(dataset)
            self.last_update_time = time.time()
            return True

        return False
    
    def is_ready_for_dispatch(self, timeout: float = 1.0) -> bool:  # change: Added function for old series
        """Check if the series is ready for dispatching, i.e. if it has not been updated for a certain timeout.
        """
        return (time.time() - self.last_update_time) > timeout


class SeriesDispatcher:
    """This code provides a template for receiving data from a modality using DICOM.
    Be sure to understand how it works, then try to collect incoming series (hint: there is no attribute indicating how
    many instances are in a series, so you have to wait for some time to find out if a new instance is transmitted).
    For simplyfication, you can assume that only one series is transmitted at a time.
    You can use the given template, but you don't have to!
    """

    def __init__(self) -> None:
        """Initialize the Series Dispatcher.
        """

        self.loop: asyncio.AbstractEventLoop
        self.modality_scp = ModalityStoreSCP()
        self.series_collector = None

    async def main(self) -> None:
        """An infinitely running method used as hook for the asyncio event loop.
        Keeps the event loop alive whether or not datasets are received from the modality and prints a message
        regulary when no datasets are received.
        """
        while True:
            # TODO: Regulary check if new datasets are received and act if they are.
            # Information about Python asyncio: https://docs.python.org/3/library/asyncio.html
            # When datasets are received you should collect and process them
            # (e.g. using `asyncio.create_task(self.run_series_collector()`)
            await self.run_series_collectors()          # change: Process incoming datasets
            await self.dispatch_series_collector()      # change: Try to send collected series
            print("Waiting for Modality")
            await asyncio.sleep(0.2)

    async def run_series_collectors(self) -> None:
        """Handles incoming datasets from the SCP."""
        dataset = self.modality_scp.get_next_dataset()  # change: Try to receive next dataset
        if dataset is None:
            return

        if self.series_collector is None:
            self.series_collector = SeriesCollector(dataset)  # change: Create collector if none exists
        else:
            added = self.series_collector.add_instance(dataset)
            if not added:
                print("Received instance from a new series. (Only one series supported at a time)")

    async def dispatch_series_collector(self) -> None:
        """Tries to dispatch a Series Collector, i.e. to finish it's dataset collection and scheduling of further
        methods to extract the desired information.
        """
        # Check if the series collector hasn't had an update for a long enough timespan and send the series to the
        # server if it is complete
        # NOTE: This is the last given function, you should create more for extracting the information and
        # sending the data to the server
        if self.series_collector and not self.series_collector.dispatch_started:
            if self.series_collector.is_ready_for_dispatch():  # change: Timeout check
                self.series_collector.dispatch_started = True
                await self.extract_and_send_metadata(self.series_collector)  # change: Send to server
                self.series_collector = None
        

    async def extract_and_send_metadata(self, collector: SeriesCollector) -> None:
        """Extracts metadata from the series and sends it as JSON to the server."""
        datasets = collector.series
        if not datasets:
            return

        first = datasets[0]
        metadata = {
            "PatientID": first.PatientID,
            "PatientName": str(first.PatientName),  # Ensures JSON serialization
            "StudyInstanceUID": first.StudyInstanceUID,
            "SeriesInstanceUID": first.SeriesInstanceUID,
            "NumInstances": len(datasets),
        }

        # change: Send metadata to server using async HTTP POST
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post("http://localhost:8000/upload-series", json=metadata)
                print(f"✅ Sent metadata: {response.status_code}")
            except Exception as e:
                print(f"❌ Failed to send metadata: {e}")


if __name__ == "__main__":
    """Create a Series Dispatcher object and run it's infinite `main()` method in a event loop.
    """
    engine = SeriesDispatcher()
    engine.loop = asyncio.get_event_loop()
    engine.loop.run_until_complete(engine.main())