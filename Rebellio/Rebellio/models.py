# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Accountsubdiffvoterecord(models.Model):
    accountname = models.CharField(db_column='AccountName', max_length=50)  # Field name made lowercase.
    songid = models.IntegerField(db_column='SongID')  # Field name made lowercase.
    difficulty = models.IntegerField(db_column='Difficulty')  # Field name made lowercase.
    subdiff = models.IntegerField(db_column='Subdiff')  # Field name made lowercase.
    createtime = models.DateTimeField(db_column='CreateTime', blank=True, null=True)  # Field name made lowercase.
    updatetime = models.DateTimeField(db_column='UpdateTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'AccountSubdiffVoteRecord'


class Accounts(models.Model):
    accountname = models.CharField(db_column='AccountName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    passwd = models.CharField(db_column='Passwd', max_length=41, blank=True, null=True)  # Field name made lowercase.
    nickname = models.CharField(db_column='Nickname', max_length=50, blank=True, null=True)  # Field name made lowercase.
    accesslevel = models.IntegerField(db_column='AccessLevel', blank=True, null=True)  # Field name made lowercase.
    id = models.IntegerField(primary_key=True)
    signature = models.TextField(db_column='signature', blank=True, null=True)
    avatar = models.IntegerField(db_column='avatar')
    skillpoint = models.IntegerField(db_column='SkillPoint')  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=32, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Accounts'

class Constants(models.Model):
    namevar = models.CharField(max_length=50, blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Constants'

class Courserecords(models.Model):
    accountname = models.CharField(db_column='AccountName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    courseid = models.IntegerField(db_column='CourseID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Courserecords'

class Gameusers(models.Model):
    userid = models.CharField(db_column='UserID', primary_key=True, max_length=6)  # Field name made lowercase.
    accountname = models.CharField(db_column='AccountName', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Gameusers'

class Packs(models.Model):
    category = models.PositiveIntegerField(db_column='Category')  # Field name made lowercase.
    packid = models.IntegerField(db_column='PackID')  # Field name made lowercase.
    title = models.TextField(db_column='Title', blank=True, null=True)  # Field name made lowercase.
    comment = models.TextField(db_column='Comment', blank=True, null=True)  # Field name made lowercase.
    haspromotion = models.IntegerField(db_column='HasPromotion', blank=True, null=True)  # Field name made lowercase.
    previewsongid = models.PositiveIntegerField(db_column='PreviewSongID', blank=True, null=True)  # Field name made lowercase.
    createtime = models.DateTimeField(db_column='CreateTime', blank=True, null=True)  # Field name made lowercase.
    id = models.IntegerField(db_column='id', primary_key=True)

    class Meta:
        managed = True
        db_table = 'Packs'
        unique_together = (('category', 'packid'),)


class Playerpackcomments(models.Model):
    id = models.IntegerField(primary_key=True)
    accountname = models.CharField(db_column='AccountName', max_length=50)  # Field name made lowercase.
    packid = models.IntegerField(db_column='PackID')  # Field name made lowercase.
    comment = models.TextField(db_column='Comment', blank=True, null=True)  # Field name made lowercase.
    createtime = models.DateTimeField(db_column='CreateTime', auto_now_add=True)  # Field name made lowercase.
    updatetime = models.DateTimeField(db_column='UpdateTime', auto_now=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'PlayerPackComments'


class Playersongcomments(models.Model):
    id = models.IntegerField(primary_key=True)
    accountname = models.CharField(db_column='AccountName', max_length=50)  # Field name made lowercase.
    songid = models.IntegerField(db_column='SongID')  # Field name made lowercase.
    comment = models.TextField(db_column='Comment', blank=True, null=True)  # Field name made lowercase.
    createtime = models.DateTimeField(db_column='CreateTime', auto_now_add=True)  # Field name made lowercase.
    updatetime = models.DateTimeField(db_column='UpdateTime', auto_now=True)  # Field name made lowercase.
    isok = models.IntegerField(db_column='IsOK')  # Field name made lowercase.
    isviewedbyauthor = models.IntegerField(db_column='IsViewedByAuthor')  # Field name made lowercase.
    authorviewtime = models.DateTimeField(db_column='AuthorViewTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'PlayerSongComments'


class Playersongfavorites(models.Model):
    accountname = models.CharField(db_column='AccountName', primary_key=True, max_length=50)  # Field name made lowercase.
    songid = models.IntegerField(db_column='SongID')  # Field name made lowercase.
    isfavorite = models.IntegerField(db_column='IsFavorite')  # Field name made lowercase.
    createtime = models.DateTimeField(db_column='CreateTime', blank=True, null=True)  # Field name made lowercase.
    updatetime = models.DateTimeField(db_column='UpdateTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'PlayerSongFavorites'
        unique_together = (('accountname', 'songid'),)


class Playrecords(models.Model):
    accountname = models.CharField(db_column='AccountName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    songid = models.IntegerField(db_column='SongID', blank=True, null=True)  # Field name made lowercase.
    difficulty = models.IntegerField(db_column='Difficulty', blank=True, null=True)  # Field name made lowercase.
    logtime = models.DateTimeField(db_column='LogTime', blank=True, null=True)  # Field name made lowercase.
    score = models.IntegerField(db_column='Score', blank=True, null=True)  # Field name made lowercase.
    jr = models.IntegerField(db_column='JR', blank=True, null=True)  # Field name made lowercase.
    note = models.IntegerField(db_column='Note', blank=True, null=True)  # Field name made lowercase.
    ar = models.FloatField(db_column='AR', blank=True, null=True)  # Field name made lowercase.
    sr = models.FloatField(db_column='SR', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Playrecords'


class Songs(models.Model):
    songid = models.IntegerField(db_column='SongID', primary_key=True)  # Field name made lowercase.
    category = models.IntegerField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    packid = models.IntegerField(db_column='PackID', blank=True, null=True)  # Field name made lowercase.
    accesslevel = models.IntegerField(db_column='AccessLevel', blank=True, null=True)  # Field name made lowercase.
    creator = models.TextField(db_column='Creator', blank=True, null=True)  # Field name made lowercase.
    title = models.TextField(db_column='Title', blank=True, null=True)  # Field name made lowercase.
    artist = models.TextField(db_column='Artist', blank=True, null=True)  # Field name made lowercase.
    chartauthorb = models.TextField(db_column='ChartAuthorB', blank=True, null=True)  # Field name made lowercase.
    chartauthorm = models.TextField(db_column='ChartAuthorM', blank=True, null=True)  # Field name made lowercase.
    chartauthor = models.TextField(db_column='ChartAuthor', blank=True, null=True)  # Field name made lowercase.
    diffb = models.IntegerField(db_column='diffB', blank=True, null=True)  # Field name made lowercase.
    diffm = models.IntegerField(db_column='diffM', blank=True, null=True)  # Field name made lowercase.
    diffh = models.IntegerField(db_column='diffH', blank=True, null=True)  # Field name made lowercase.
    diffsp = models.IntegerField(db_column='diffSP', blank=True, null=True)  # Field name made lowercase.
    subdiffb = models.IntegerField(db_column='subdiffB', blank=True, null=True)  # Field name made lowercase.
    subdiffm = models.IntegerField(db_column='subdiffM', blank=True, null=True)  # Field name made lowercase.
    subdiffh = models.IntegerField(db_column='subdiffH', blank=True, null=True)  # Field name made lowercase.
    subdiffsp = models.IntegerField(db_column='subdiffSP', blank=True, null=True)  # Field name made lowercase.
    hasspecial = models.IntegerField(db_column='HasSpecial', blank=True, null=True)  # Field name made lowercase.
    specialid = models.IntegerField(db_column='SpecialID', blank=True, null=True)  # Field name made lowercase.
    sequencepid = models.IntegerField(db_column='SequencePID', blank=True, null=True)  # Field name made lowercase.
    createtime = models.DateTimeField(db_column='CreateTime', blank=True, null=True)  # Field name made lowercase.
    updatetime = models.DateTimeField(db_column='UpdateTime', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    authordescription = models.TextField(db_column='AuthorDescription', blank=True, null=True)  # Field name made lowercase.
    isvotingsubdiff = models.IntegerField(db_column='IsVotingSubdiff')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Songs'


class Unlockrecords(models.Model):
    accountname = models.CharField(db_column='AccountName', primary_key=True, max_length=50)  # Field name made lowercase.
    songid = models.IntegerField(db_column='SongID')  # Field name made lowercase.
    pid = models.IntegerField(db_column='PID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Unlockrecords'
        unique_together = (('accountname', 'songid'),)


class ClassCheckRecords(models.Model):
    accountname = models.CharField(db_column='AccountName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    class_field = models.IntegerField(db_column='Class', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    clearlevel = models.IntegerField(db_column='ClearLevel', blank=True, null=True)  # Field name made lowercase.
    logtime = models.DateTimeField(db_column='LogTime', blank=True, null=True)  # Field name made lowercase.
    achievementrate = models.FloatField(db_column='AchievementRate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'class_check_records'

