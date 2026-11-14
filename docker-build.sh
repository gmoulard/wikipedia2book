#!/bin/sh
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

docker build \
  --build-arg GIT_COMMIT="$(git log -1 --format=%H)" \
  --build-arg GIT_DATE="$(git log -1 --format=%ci)" \
  --build-arg GIT_AUTHOR="$(git log -1 --format=%an)" \
  -t wikipedia2book .
