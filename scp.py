# Datei: scp.py

from pydicom.dataset import FileMetaDataset
from pynetdicom import AE, events, evt, debug_logger
from pynetdicom.sop_class import MRImageStorage
from queue import Queue  # threadsave Queue instead Lock

debug_logger()  # Enables detailed DICOM networking logs


class ModalityStoreSCP():
    """
    Implements a simple DICOM Storage SCP (Service Class Provider)
    that receives DICOM instances and queues them for processing.
    """

    def __init__(self) -> None:
        self.ae = AE(ae_title=b'STORESCP')
        self.scp = None
        self._dataset_queue = Queue() # change: Thread-safe queue for the dataset queue
        self._configure_ae()

    def _configure_ae(self) -> None:
        """Configure the Application Entity with the presentation context(s) which should be supported and start the SCP server.
        """
        handlers = [(evt.EVT_C_STORE, self.handle_store)]

        self.ae.add_supported_context(MRImageStorage)
        self.scp = self.ae.start_server(('127.0.0.1', 6667), block=False, evt_handlers=handlers)
        print("SCP Server started")

    def handle_store(self, event: events.Event) -> int:
        """Callable handler function used to handle a C-STORE event.

        Args:
            event (Event): Representation of a C-STORE event.

        Returns:
            int: Status Code
        """
        dataset = event.dataset
        dataset.file_meta = FileMetaDataset(event.file_meta)

        # TODO: Do something with the dataset. Think about how you can transfer the dataset from this place 
        # to the main thread or another thread for further processing.

        self._dataset_queue.put(dataset)

        return 0x0000  # change: Status code for success

        
    def get_next_dataset(self):
        """Get the next dataset from the queue in a thread-safe manner.
        Returns:
            Dataset: The next dataset in the queue or None if the queue is empty.
        """
        
    def get_next_dataset(self):
        if not self._dataset_queue.empty():
           return self._dataset_queue.get()
        return None
