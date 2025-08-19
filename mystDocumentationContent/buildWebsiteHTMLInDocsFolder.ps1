# Set the BASE_URL environment variable to a placeholder address
$env:BASE_URL = "https://klemet.github.io/Workshop-MagicHarvest"

# Build the HTML files
myst build --html

# Define the source and destination directories
$sourceDir = "_build/html"
$destDir = "../docs"

# Delete the destination directory if it exists
if (Test-Path -Path $destDir) {
    Remove-Item -Path $destDir -Recurse -Force
}

# Create the destination directory
New-Item -ItemType Directory -Path $destDir

# Copy all files and subdirectories from the source directory to the destination directory
Copy-Item -Path $sourceDir\* -Destination $destDir -Recurse

# Output a message indicating the operation is complete
Write-Host "All files and subdirectories have been successfully moved to the $destDir folder."