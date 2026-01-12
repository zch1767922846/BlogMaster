# -*- coding: utf-8 -*-
# File: page_resource.py
# Author: Zhangzhijun
# Date: 2021/2/13 17:22
from flask import current_app

from app.errors.errorcode import ResponseCode, ResponseMessage
from app.models.page import Page
from app.models.user import User
from app.utils import query_to_dict


class PageResource():
    @staticmethod
    def query_pages():
        try:
            pages = Page.query(Page.id, Page.title, Page.slug, User.username, Page.publishtime) \
                .filter(Page.authorid == User.id) \
                .all() \
                .order_by(Page.publishtime.desc())
        except:
            current_app.logger.debug("query db filed!")
            return dict(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)
        if pages is None:
            current_app.logger.debug("page is none!")
            return dict(code=ResponseCode.PAGE_NOT_EXIST, message=ResponseMessage.PAGE_NOT_EXIST)
        current_app.logger.debug("pages: %s", pages)
        data = dict(code=ResponseCode.SUCCESS, message=ResponseMessage.SUCCESS, data=query_to_dict(pages))
        current_app.logger.debug("data: %s", data)
        return data

    @staticmethod
    def query_page_by_id(page_id):
        try:
            page = Page.query(Page.id, Page.title, Page.slug, User.username, Page.excerpt,
                              Page.updatetime) \
                .filter(Page.id == page_id) \
                .filter(Page.authorid == User.id) \
                .first()
        except:
            return dict(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)

        if page is None:
            return dict(code=ResponseCode.PAGE_NOT_EXIST, message=ResponseMessage.PAGE_NOT_EXIST)
        current_app.logger.debug("page: %s", p)
        data = dict(code=ResponseCode.SUCCESS, message=ResponseMessage.SUCCESS, data=query_to_dict(page))
        current_app.logger.debug("data: %s", data)
        return data

    # get Page by Page name
    @staticmethod
    def query_page_by_title(title):
        try:
            pages = Page.query(Page.id, Page.title, Page.slug, User.username, Page.excerpt,
                               Page.updatetime) \
                .filter(Page.title == title) \
                .filter(Page.authorid == User.id) \
                .all()
        except:
            return dict(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)
        if pages is None:
            return dict(code=ResponseCode.PAGE_NOT_EXIST, message=ResponseMessage.PAGE_NOT_EXIST)
        current_app.logger.debug("posts: %s", pages)
        data = dict(code=ResponseCode.SUCCESS, message=ResponseMessage.SUCCESS, data=query_to_dict(pages))
        current_app.logger.debug("data: %s", data)
        return data

    # get Pages by author

    @staticmethod
    def query_page_by_author(author):
        try:
            author = User.query.filter_by(username=author).first()
            pages = Page.query(Page.id, Page.title, Page.slug, User.username, Page.excerpt,
                               Page.updatetime) \
                .filter(Page.authorid == author.id) \
                .all()
        except:
            return dict(code=ResponseCode.QUERY_DB_FAILED, message=ResponseMessage.QUERY_DB_FAILED)
        if pages is None:
            return dict(code=ResponseCode.PAGE_NOT_EXIST, message=ResponseMessage.PAGE_NOT_EXIST)
        current_app.logger.debug("posts: %s", pages)
        data = dict(code=ResponseCode.SUCCESS, message=ResponseMessage.SUCCESS, data=query_to_dict(pages))
        current_app.logger.debug("data: %s", data)
        return data
