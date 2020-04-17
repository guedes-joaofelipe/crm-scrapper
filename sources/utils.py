from datetime import datetime
import sys

class ProgressBar:
    """ A class to show clean progress bar    
    """    

    def __init__(self, bar_length = 10, bar_fill = '#', elapsed_time=False):
        """ Initializing the class
        
        Keyword Arguments:
            bar_length {int} -- (default: {10})
            bar_fill {str} -- character to fill the bar (default: {'#'})
            elapsed_time {bool} -- whether or not to show elapsed time (default: {False})
        """        

        self.bar_length = bar_length
        self.bar_fill = bar_fill
        self.status = ""
        self.last_progress = 0
        self.elapsed_time = elapsed_time

        if (elapsed_time):
            self.last_update = None
            self.start_time = None

    def update_progress(self, progress = 0.0):
        """ Function to update the shown progress bar
        
        Keyword Arguments:
            progress {float} -- float between 0 and 1 refering the percentage of progress 
                (default: {0})
        """        

        self.status = ""
        self.last_progress = progress

        if isinstance(progress, int):
            progress = float(progress)

        if not isinstance(progress, float):
            progress = 0
            self.status = "error: progress var must be float\r\n"

        if progress < 0:
            progress = 0
            self.status = "Halt...\r\n"

        if progress >= 1:
            progress = 1
            self.status = "Done...\r\n"

        block = int(round(self.bar_length*progress))

        if (self.elapsed_time):
            if (progress == 0):
                self.start_time = datetime.now()

            self.last_update = datetime.now()

        if (self.elapsed_time and self.last_update is not None):
            text = "\r[{0}][{1}] {2:.2f}% {3}".format(str(self.last_update-self.start_time).split('.')[0], self.bar_fill*block + "-"*(self.bar_length-block), progress*100, self.status)
        else:
            text = "\rPercent: [{0}] {1:.2f}% {2}".format( self.bar_fill*block + "-"*(self.bar_length-block), progress*100, self.status)
            
        sys.stdout.write(text)
        sys.stdout.flush()

    def get_last_progress(self):
        return self.last_progress

    def get_elapsed_time(self):
        return str(self.last_update-self.start_time).split('.')[0]