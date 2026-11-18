# This file is part of Wikipedia2Book
# <https://github.com/gmoulard/wikipedia2book>.
# Copyright (c) 2026 Guillaume Moulard.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

param(
    [int]$Port = 4000,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$name = "wikipedia2book-docs"
$image = "ruby:3.3.6"
$docs = $PSScriptRoot

$docker = (Get-Command docker -ErrorAction SilentlyContinue).Source
if (-not $docker) {
    $docker = @(
        "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin\docker.exe",
        "$env:ProgramFiles\Docker\Docker\resources\bin\docker.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $docker) { throw "docker.exe introuvable : installez Docker Desktop." }

function Test-Engine {
    & $docker version --format "{{.Server.Version}}" *> $null
    return $LASTEXITCODE -eq 0
}

if (-not (Test-Engine)) {
    $desktop = @(
        "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe",
        "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $desktop) { throw "Docker Desktop introuvable : démarrez le moteur Docker puis relancez." }
    Write-Host "Démarrage de Docker Desktop..."
    Start-Process $desktop
    $deadline = (Get-Date).AddMinutes(3)
    while (-not (Test-Engine)) {
        if ((Get-Date) -gt $deadline) { throw "Le moteur Docker n'a pas démarré en 3 minutes." }
        Start-Sleep -Seconds 3
    }
}

& $docker rm -f $name *> $null

$script = @'
set -e
cat > /tmp/Gemfile <<'GEMS'
source "https://rubygems.org"
gem "github-pages", group: :jekyll_plugins
gem "webrick"
GEMS
export BUNDLE_GEMFILE=/tmp/Gemfile
bundle install --quiet
exec bundle exec jekyll serve --source /site --destination /tmp/_site --host 0.0.0.0 --port 4000 --baseurl "" --livereload --force_polling
'@ -replace "`r", ""

$arguments = @(
    "run", "-d", "--name", $name,
    "-p", "${Port}:4000", "-p", "35729:35729",
    "-v", "${docs}:/site:ro",
    "-v", "wikipedia2book-docs-gems:/usr/local/bundle",
    "-e", "JEKYLL_ENV=development", "-e", "PAGES_REPO_NWO=gmoulard/wikipedia2book"
)
foreach ($variable in "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY") {
    $value = [Environment]::GetEnvironmentVariable($variable)
    if ($value) { $arguments += @("-e", "$variable=$value") }
}
$arguments += @($image, "bash", "-c", $script)

& $docker @arguments | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Le conteneur n'a pas démarré." }

$url = "http://localhost:$Port/"
Write-Host "Construction du site (la première fois, installation des gems : quelques minutes)..."
try {
    $ready = $false
    while (-not $ready) {
        $state = & $docker inspect -f "{{.State.Running}}" $name 2>$null
        if ($state -ne "true") {
            & $docker logs $name
            throw "Le conteneur s'est arrêté."
        }
        try {
            Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 3 | Out-Null
            $ready = $true
        } catch {
            Start-Sleep -Seconds 3
        }
    }
    Write-Host "Site prêt : $url (rechargé à chaque modification de docs/). Ctrl+C pour arrêter."
    if (-not $NoBrowser) { Start-Process $url }
    & $docker logs -f --since 1s $name
} finally {
    & $docker rm -f $name *> $null
    Write-Host "Conteneur arrêté."
}
