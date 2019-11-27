from Jumpscale import j

from .Link import Linker
from .DocSite import DocSite, Doc

JSBASE = j.baseclasses.object


class ThreeGitFactory(j.baseclasses.object):
    """
    To get wikis load faster by only loading git changes
    """

    # TODO: Add required bcdb configs

    __jslocation__ = "j.tools.threegit"

    def _init(self, **kwargs):
        self.dest = kwargs.get("dest", "")
        self._macros_modules = {}  # key is the path
        self._macros = {}  # key is the name
        self.docsites = {}

    def macros_load(self, path_or_url=None):
        # TODO: ADD current macros [filesystem changes]
        """
        @param path_or_url can be existing path or url
        """
        self._log_info("load macros:%s" % path_or_url)

        if not path_or_url:
            path_or_url = (
                "https://github.com/threefoldtech/jumpscaleX_libs/tree/*/JumpscaleLibs/tools/markdowndocs/macros"
            )

        path = j.clients.git.getContentPathFromURLorPath(path_or_url)

        if path not in self._macros_modules:

            if not j.sal.fs.exists(path=path):
                raise j.exceptions.Input("Cannot find path:'%s' for macro's, does it exist?" % path)

            for path0 in j.sal.fs.listFilesInDir(path, recursive=False, filter="*.py", followSymlinks=True):
                name = j.sal.fs.getBaseName(path0)[:-3]  # find name, remove .py
                self._macros[name] = j.tools.jinja2.code_python_render(
                    obj_key=name, path=path0, reload=False, objForHash=name
                )

    def find_docs_path(self, path, base_path="docs"):
        """try to find docs path from base_path inside a given repo path and return it if exists

        :param path: repo path, e.g. `/sandbox/code/github/threefoldfoundation/info_foundation`
        :param base_path: dir inside the repo which has the md files will be joined with repo path
        :type path: str
        """
        gitpath = j.clients.git.findGitPath(path)
        if not gitpath or gitpath != path:
            return path

        docs_path = j.sal.fs.joinPaths(path, base_path)
        if j.sal.fs.exists(docs_path):
            return docs_path
        return path

    def load(self, path="", name="", dest="", base_path="docs", pull=False, download=False):
        self.macros_load()
        if path.startswith("http"):
            # check if we already have a git repo, then the current checked-out branch
            repo_args = j.clients.git.getGitRepoArgs(path)
            host = repo_args[0]
            dest = repo_args[-3]
            repo_dest = j.clients.git.findGitPath(dest, die=False)
            if repo_dest:
                # replace branch with current one
                current_branch = j.clients.git.getCurrentBranch(repo_dest)
                path = Linker.replace_branch(path, current_branch, host)
            path = self.find_docs_path(j.clients.git.getContentPathFromURLorPath(path, pull=pull), base_path)
        ds = DocSite(path=path, name=name, dest=dest)
        self.docsites[ds.name] = ds
        return self.docsites[ds.name]

    def process(self, path_source, path_dest, check=True, force=True):
        """
        # 1- TODO: Load macros
        # 2- TODO: write docsites [integrate with 3git configs]
        # 3- TODO: process docsites with macros
        # 4- TODO: if check = True
                # Load latest files changes
        # 5- TODO: if force = True
               # Reload all docsites
        :param path_source: source of gitrepo / docsite files
        :param path_dest: destination to save docsites files in it
        :param check: reload changed files in docsite since last ref
        :param force: Reload all docsites files and reparse them
        :return:
        """

        j.shell()
