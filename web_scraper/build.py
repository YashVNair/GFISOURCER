import subprocess
import os
import platform

def get_separator():
    """Returns the appropriate path separator for the OS."""
    return ';' if platform.system() == 'Windows' else ':'

def run_pyinstaller():
    """Runs the PyInstaller command to build the executable."""
    # Base directory of the application
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the main script
    script_path = os.path.join(base_dir, 'gui.py')

    # Name for the output executable
    app_name = "Smart Protein Scraper"

    # PyInstaller command arguments
    command = [
        'pyinstaller',
        '--name', app_name,
        '--onefile',
        '--windowed', # Use '--noconsole' for a GUI app
        f'--add-data={os.path.join(base_dir, "product_scraper")}{get_separator()}product_scraper',
        f'--add-data={os.path.join(base_dir, "companies.csv")}{get_separator()}.',
        # Many hidden imports are needed for Scrapy to work correctly when bundled.
        '--hidden-import=scrapy.spiders',
        '--hidden-import=scrapy.extensions',
        '--hidden-import=scrapy.utils',
        '--hidden-import=scrapy.contracts',
        '--hidden-import=scrapy.item',
        '--hidden-import=scrapy.loader',
        '--hidden-import=scrapy.selector',
        '--hidden-import=scrapy.linkextractors',
        '--hidden-import=scrapy.core.downloader.handlers.http',
        '--hidden-import=scrapy.core.downloader.handlers.http2',
        '--hidden-import=scrapy.core.downloader.contextfactory',
        '--hidden-import=scrapy.pipelines',
        '--hidden-import=scrapy.statscollectors',
        '--hidden-import=scrapy.logformatter',
        '--hidden-import=scrapy.dupefilters',
        '--hidden-import=scrapy.core.scheduler',
        '--hidden-import=scrapy.squeues',
        '--hidden-import=scrapy.core.engine',
        '--hidden-import=scrapy.extensions.logstats',
        '--hidden-import=scrapy.extensions.corestats',
        '--hidden-import=scrapy.extensions.telnet',
        '--hidden-import=scrapy.extensions.memusage',
        '--hidden-import=scrapy.extensions.memdebug',
        '--hidden-import=scrapy.extensions.feedexport',
        '--hidden-import=scrapy.extensions.closespider',
        '--hidden-import=scrapy.extensions.debug',
        '--hidden-import=scrapy.extensions.httpcache',
        '--hidden-import=scrapy.extensions.statsmailer',
        '--hidden-import=scrapy.extensions.throttle',
        '--hidden-import=scrapy.core.spidermw',
        '--hidden-import=scrapy.spidermiddlewares.httperror',
        '--hidden-import= scrapy.spidermiddlewares.offsite',
        '--hidden-import=scrapy.spidermiddlewares.referer',
        '--hidden-import=scrapy.spidermiddlewares.urllength',
        '--hidden-import=scrapy.spidermiddlewares.depth',
        '--hidden-import=scrapy.core.downloadermw',
        '--hidden-import=scrapy.downloadermiddlewares.stats',
        '--hidden-import=scrapy.downloadermiddlewares.httpauth',
        '--hidden-import=scrapy.downloadermiddlewares.downloadtimeout',
        '--hidden-import=scrapy.downloadermiddlewares.useragent',
        '--hidden-import=scrapy.downloadermiddlewares.retry',
        '--hidden-import=scrapy.downloadermiddlewares.ajaxcrawl',
        '--hidden-import=scrapy.downloadermiddlewares.defaultheaders',
        '--hidden-import=scrapy.downloadermiddlewares.redirect',
        '--hidden-import=scrapy.downloadermiddlewares.cookies',
        '--hidden-import=scrapy.downloadermiddlewares.httpcompression',
        '--hidden-import=scrapy.downloadermiddlewares.chunked',
        '--hidden-import=scrapy.downloadermiddlewares.httpcache',
        '--hidden-import=scrapy.downloadermiddlewares.robotstxt',
        # Hidden import for a dependency of Scrapy
        '--hidden-import=pkg_resources.py2_warn',
        script_path
    ]

    print("Running PyInstaller...")
    print(" ".join(command))

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("\nBuild successful!")
        print(f"Executable created in the '{os.path.join(base_dir, 'dist')}' directory.")
    except subprocess.CalledProcessError as e:
        print("\n--- Build Failed ---")
        print(f"PyInstaller exited with error code: {e.returncode}")
        print("\n--- STDOUT ---")
        print(e.stdout)
        print("\n--- STDERR ---")
        print(e.stderr)
        print("\n------------------")
    except FileNotFoundError:
        print("\nError: `pyinstaller` command not found.")
        print("Please make sure PyInstaller is installed (`pip install pyinstaller`) and is in your system's PATH.")

if __name__ == "__main__":
    run_pyinstaller()
