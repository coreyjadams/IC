How to contribute to IC
=======================

Prepare github
--------------

- `Get a github account
  <https://help.github.com/articles/signing-up-for-a-new-github-account/>`_
  if you do not already have one.

- `Upload your SSH key
  <https://help.github.com/articles/generating-an-ssh-key/>`_, if
  you have not already done so.

Prepare your repositories
-------------------------

TODO

- Fork the IC repository

- Clone your fork

- set nextic as *upstream*

Use a higher-level git interface
--------------------------------

Do yourself a favour, and use `magit <https://magit.vc/>`_ to interact
with git: `it's the best git UI <https://magit.vc/quotes/>`_ on the
planet. Even if you don't use or dislike Emacs, use magit, and think
of Emacs as the GUI framework in which magit is written.

You will enjoy and learn to understand git much more if you use magit.

[Editor's note: Seriously, I tried to find something to recommend for
those who don't use Emacs. It wasted a lot of my time, and I came to
the conclusion that recommending anything else would be a waste of
**your** time. Just use magit.]

To make the magit experience even better, use
`helm <https://emacs-helm.github.io/helm/>`_.

History philosophy
------------------

In `the words of <https://sandofsky.com/blog/git-workflow.html>`_ Ben
Sandofsky:

::

 Treat public history as immutable, atomic, and easy to follow. Treat
 private history as disposable and malleable.

 The intended workflow is:

  1. Create a private branch off a public branch.
  2. Regularly commit your work to this private branch.
  3. Once your code is perfect, clean up its history.
  4. Merge the cleaned-up branch back into the public branch.

- In IC, step 4 is done by the IC administators *after the work has
  been reviewed and approved*, so you don't have to worry about this
  step for now.

- The history that appears in your local clone (your private history)
  is there entirely for *your* benefit. As such, it is malleable and
  disposable, and you can modify it however and whenever you like.

- The history that appears in the central nextic repository serves as
  a clean, high-level description of the evolution of the project,
  where

  - it should be easy to find where and when something was changed,
    added, removed, where bugs were introduded (perhaps using tools
    such as `git bisect <https://git-scm.com/docs/git-bisect>`_),

  - a high-level description of the changes should be available.

  As such, the central history should

  - be linear,

  - contain very descriptive commit messages describing and
    documenting the changes.

- The commits that appear in your fork on github can serve a number of
  purposes:

  - A place from which you submit pull requests, asking for your
    contribution to be incorporated into the main repository. (The
    commits that appear in pull requests should therefore conform to
    the high standards required by the main history: clean, linear
    (usually squashed) and documented with descriptive commit
    messages.)

  - Triggers of travis builds, checking that your work builds and
    passes all the tests in a clean environment.

  - Sharing your work with other developers and collaborating on
    development with others *before* submitting a pull request.


Workflow summary
----------------

1. Create a topic branch starting at ``upstream/master`` in your local
   repo.

2. Make numerous checkpoint commits to your topic branch.

3. Write tests for the code you write.

4. Push the topic branch to your github fork (origin) whenever you
   want feedback from Travis.

5. In preparation for making a pull request (PR), squash the
   checkpoint commits into a smaller number of logically
   self-contained commits with descriptive, high-level commit
   messages. Try to make each commit (and its diff) tell a story that
   will be easily understood by the reviewers.

6. Fetch (whatever you do, **do not pull**) ``upstream/master`` into
   your local repository..

7. Rebase your topic branch onto ``upstream/master``.

8. Push the branch to ``origin``.

9. a pull request (PR) from your github page.

10. Wait for the PR to be approved and merged.

11. Fetch ``upstream/master`` into your local repo.

12. Delete your topic branch, both locally and in your fork.

13. GOTO 1


Workflow in detail
------------------

In what follows, the commands required to achieve the effect will be
given in two styles (eventually; initially the git CLIs are likely to
be TODOs).

1. magit
2. git command line interface (CLI)

In the case of magit you should type the instructions in some magit
buffer inside Emacs. If no such buffer is visible, create the magit
status buffer with ``M-x magit-status``. This last command must be
given in some buffer linked to a file or directory inside the relevant
git repository.

Magit buffers can usually be closed with ``q``. Emacs commands in
general can be interrupted with ``C-g``.

In the case of the git CLI, you should type the commands in a shell
whose working directory is inside there relevant git repository.

1. Before starting some new work, make sure that you have the most
   recent IC code.

   - magit: ``f e upstream RET``

     - ``f`` opens the magit fetching popup
     - ``e`` allows you to specify the remote from which you would
       elike to fetch
     - ``upstream`` specifies that you want to fetch from the central
       nextic repository. (This assumes that you have already added
       ``upstream`` as a remote pointing at ``nextic/IC`` in your
       local repository)

   - git CLI: ``git fetch upstream``

2. Create a topic branch.

   In the following examples replace 'topic' with whatever name you
   want to give to your branch. The name sohuld be meaningful to you
   and identify the work that you are doing. You may end up having
   multiple topic branches in existence simultaneously, so picking
   good names will make life easier for *you*.

   - magit: ``b c upstream/master RET topic RET``

     - ``b`` opens the magit branch popup
     - ``c`` creates and checks out a new branch
     - ``upstream/master`` is the location from which you want to branch off
     - ``topic`` is the name of your new branch

   - git CLI: ``git checkout -b topic upstream/master``

   Magit will walk you through these steps interactively. Helm, if
   you've installed it, will improve the interactive experience. If
   you make a mistake magit will help you avoid digging yourself into
   a deeper hole. With the git CLI you are on your own.

3. Create plenty of checkpoint commits while you are working. Frequent
   checkpoint commits ensure that, if you ever get yourself into a
   complete mess, you can get out of it cheaply by reverting to a
   *recent* sensible state.

   This is how to do a local commit

   - magit:

     - ``M-x magit-status`` (or your keybinding, possibly ``C-x g``)

       Opens the magit status buffer, showing you (among other things)

         - which files have been modified since the last commit
         - which files have been deleted since the last commit
         - which files exist but are not registered in the repository

       The most useful keys inside this buffer are

         - ``s``: stage - include this in the next commit
         - ``u``: unstage - undo a previous stage
         - ``n``: next - move to the next interesting location
         - ``p``: previous - move to the previous interesting location
         - ``c``: commit - start the commit process
         - ``d``: diff - open the magit diff popup

       So, you should specify what you want to be included in the
       commit by staging it. Then proceed with the commit with ``c``,
       at which point a commit message buffer should appear, with
       self-explanatory comments inside it. In short, write a commit
       message and then perform the commit with ``C-c C-c``.

       When you get around to creating a pull request, you should
       squash (see below) your checkpoint commit messages into a
       smaller number of coherent, clean, commits with descriptive
       commit messages describing your work. The purpose of the
       checkpoint commit messages is to make authoring the pull
       request commit messages as easy as possible.

   - git CLI: TODO

4. Make sure that the code you contribute is adequately tested. See
   below.

5. Whenever you want to see whether your current code builds and
   passes all the required tests in a clean environment, commit
   (described above) and push to your fork (origin).

   - magit:

      - The first time in a new branch: ``P p origin RET``

      - Thereafter: ``P p``

      ``P`` opens the magit push popup. Once there, ``p`` pushes to
      the remote which needs to be set once for each branch.

   - git CLI: TODO

6. Once you have achieved something worth incorporating into the main
   repository, it's time to make a pull request (PR). Usually your
   pull request should consist of a smaller number of commits than you
   originally made during development, each with a carefully written,
   high-level, descriptive commit message describing your work. The
   commit message of a single-commit PR is taken as the default PR
   description text. If your PR contains more than one commit, you
   should create a description of the whole collection in the GitHub
   PR interface.

   You should squash your numerous checkpoint commits to make cleaner
   PR commits.

   - magit:

     - ``l l``: the first ``l`` opens the magit log popup, the second
       shows the log for the current branch only

     - navigate down to the first commit in your branch with ``n`` and
       ``p`` (which stand for [n]ext and [p]revious line)

     - ``r i``: opens the magit rebase popup and selects interactive
       rebase. This will give you a buffer listing all the commits in
       the range you specified, accompanied by comments which explain
       what can be done. Typically you will want to do something like

       - ``n s s s s C-c C-c``

         The ``n`` moves the cursor down to the **n**\ ext commit
         (because you want to leave the default action (pick) for the
         first (earliest) commit).

         The subsequent ``s``\ s change the action for the subsequent
         commits to **s**\ quash. This will incorporate the changes
         that appeared in the squashed commits, into the last
         unsquashed commits before them.

         Finally, ``C-c C-c`` instructs magit to perform the actions
         specified in the buffer. At this point you will get a commit
         buffer (you should be familiar with this from your checkpoint
         commits) containing a union of *all* the commit messages
         corresponding to the commits you have picked and
         squashed. Edit this carefully to make a single, clean,
         high-level, descriptive commit message describing the work
         you are proposing for inclusion in the main repository. If
         you have squashed everything down to a single commit, this
         message will be proposed to you as the default PR description
         message.

         When you are satisfied with your commit message, complete the
         commit with

       - ``C-c C-c``

7. Fetch the latest developments on ``upstream/master``. (You already
   did this in step 1.)

   - magit: 

      - ``f e upstream RET``

   - git CLI: ``git fetch upstream``

8. Rebase your topic branch onto ``upstream/master``

   - magit:

      - ``b b topic RET``: checkout ``topic``

      - ``r e master``: rebase current branch (``topic``) onto ``master``

   - git CLI: TODO

   At this point, you may discover that new additions to the main
   repository conflict with your work. If this happens, abort the
   rebase

   - magit: ``r a y`` ([r]ebase [a]bort [y]es)  

   and proceed with the PR without rebasing. These conflicts will need
   to be resolved and your commits will have to rebased eventually,
   but, at this stage, it's best not to try it on your own if these
   complications arise: let some IC admin help you or do it for you on
   your first attempts.

9. Push your clean pull request-ready (PR) commits to your github fork

   - magit: ``P -f p``

     TODO: Need to mention

       - forcing
       - the need to set pushRemote at least once per branch

   - git CLI: TODO

10. Submit a pull request (PR) from your github page.

   TODO: Is it worth writing anything here, or is github sufficiently
   self-explanatory on this topic?

11. Once your PR has been merged, you should receive an automatic
    email from github. Once your PR has been merged you can proceed to
    clean up as follows.

12. Fetch the latest ``upstream/master`` into your local clone. (We've
    done this before in steps 1. and 7.)

   - magit:

      - ``f e upstream RET``

13. Delete your topic branch, both locally and in your fork.

   - magit:

     - ``b k topic RET``
     - ``b k origin/topic RET``
     - ``b k origin/topic RET`` : Yes! The same thing twice!  The
       first on removes the branch on the remote, once that has gone,
       the second removes your local tracking branch.

        - git CLI: TODO

14. That's it. Now you can repeat the process all over again for some
    new work.

    Don't forget that you can interleave work on different branches:
    you can start work on some other branch before completing this
    cycle on your first branch. You can switch contexts by checking
    out the branch on which you want to work right now. If there is
    some uncommited work on the branch you were working on previously,
    you will have to do one of the following

    - commit it

    - stash it

    before git will allow you to switch to another branch.


Testing
-------

Write tests for any new code that you write. Before your code can be
merged into the main repository it must be reviewed by someone
else. Expect reviewers to reject your code if it does not come with
adequate tests.

By default, tests for ``invisible_cities/whatever/stuff.py`` should be
in ``invisible_cities/whatever/stuff_test.py``.

Tests serve a number of purposes:

1. Point out when something that worked before has been broken.

2. Help the author of the code understand what the code is supposed to
   do.

   This is a frequently underappreciated aspect of tests. On many
   occasions, the process of devising, writing and passing tests leads
   to a much better understanding of the tested code and the domain it
   addresses.

3. Act as documentation.

   While this is not the primary goal of tests, well written tests can
   be an excellent form of documentation. Try to write your tests in a
   way that makes them easy to understand for a human reader and that
   makes the behaviour and purpose of the tested code as clear as
   possible.

Code that has made it into the central repository should already have
accompanying tests. Before starting any work, make sure that the code
you checked out passes all the tests. In the (hopefully extremely
unlikely case) that it does not, contact the author of the failing
code and make sure that a fix is uploaded to the central repository as
soon as possible.

Conversely, make sure that any pull requests you submit pass all
tests. Enabling Travis in your fork will give you an early
warning. Travis automatically runs on any pull requests submitted to
the nextic main repository, and the repository configuration prevents
merging pull requests which contain failing tests.

**Submitting code without tests is equivalent to saying that you don't
mind if the code is broken by someone else!**


Style guide
-----------

Follow PEP8, but bear in mind that the most important part of PEP8 is:

TODO copypasta n link to the "Readability is more important than any
of these rules"
